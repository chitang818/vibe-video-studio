using System.Security.Cryptography;
using System.Text.Json;
using WeMediaForge.Application.Models.WebProcess;

namespace WeMediaForge.Application.Helpers;

/// <summary>Shared page/workflow preflight. The manifest, not filename guesses, owns project identity.</summary>
public static class VibeProjectReader
{
    public const string ManifestName = "vibe.project.json";
    public const string RuntimeVersion = "1.2.0";
    public const string RuntimeFile = "vibe-runtime/scene.mjs";
    public static async Task<VibeProject> LoadAsync(string input, CancellationToken ct = default)
    {
        ct.ThrowIfCancellationRequested();
        var full = Path.GetFullPath(input);
        var root = Directory.Exists(full) ? full : Path.GetDirectoryName(full)!;
        if (!Directory.Exists(root)) throw new InvalidDataException("工程目录不存在。");
        var manifestPath = Path.Combine(root, ManifestName);
        if (!File.Exists(manifestPath)) throw new InvalidDataException("这是旧版网页工程，请通过制作工具重新生成高速视频工程后导入。");
        if (new FileInfo(manifestPath).Length > 1024 * 1024) throw new InvalidDataException("工程清单过大。");
        var manifest = JsonSerializer.Deserialize<VibeProjectManifest>(await File.ReadAllTextAsync(manifestPath, ct), JsonOptions)
            ?? throw new InvalidDataException("工程清单为空。");
        if (manifest.SchemaVersion != 1 || manifest.RuntimeVersion != RuntimeVersion || manifest.RuntimeSha256 != VibeRuntimeIdentity.Sha256)
            throw new InvalidDataException("工程版本与当前软件不匹配，请更新制作工具后重新打包。");
        if(manifest.AssetHashes is null || string.IsNullOrWhiteSpace(manifest.HtmlFile) || string.IsNullOrWhiteSpace(manifest.SceneFile))
            throw new InvalidDataException("工程清单缺少必要文件信息。");
        if (string.IsNullOrWhiteSpace(manifest.Title) || manifest.Width is < 64 or > 3840 || manifest.Height is < 64 or > 3840 ||
            manifest.Width % 2 != 0 || manifest.Height % 2 != 0 || manifest.DurationUs is <= 0 or > 7_200_000_000)
            throw new InvalidDataException("工程标题、画幅或时长无效。");
        var required = new[] { manifest.HtmlFile, manifest.SceneFile, RuntimeFile, manifest.VoiceFile, manifest.TimestampsFile, manifest.ScriptFile, manifest.SfxFile }.Where(p => p is not null).Cast<string>().ToArray();
        foreach (var path in required)
            if (!manifest.AssetHashes.ContainsKey(path)) throw new InvalidDataException("工程清单缺少文件校验信息，请重新打包。");
        if (manifest.AssetHashes.Count > 2048) throw new InvalidDataException("工程素材过多。");
        foreach (var (relative, hash) in manifest.AssetHashes)
        {
            var path = ResolveAsset(root, relative);
            if (!File.Exists(path)) throw new InvalidDataException("工程素材缺失，请重新打包。");
            await using var stream = File.OpenRead(path);
            var actual = Convert.ToHexString(await SHA256.HashDataAsync(stream, ct));
            if (!string.Equals(actual, hash, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("工程素材已更改，请重新打包后导入。");
        }
        if (!string.Equals(manifest.AssetHashes[RuntimeFile], VibeRuntimeIdentity.Sha256, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("工程渲染组件校验失败。");
        if (File.Exists(full) && !Path.GetFileName(full).Equals(ManifestName, StringComparison.OrdinalIgnoreCase) &&
            !string.Equals(full, ResolveAsset(root, manifest.HtmlFile), StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("所选网页不属于该工程清单。");
        var scenePath = ResolveAsset(root, manifest.SceneFile);
        if (new FileInfo(scenePath).Length > 8 * 1024 * 1024) throw new InvalidDataException("场景数据过大。");
        using var scene = JsonDocument.Parse(await File.ReadAllTextAsync(scenePath, ct));
        if (!scene.RootElement.TryGetProperty("scenes", out var scenes) || scenes.ValueKind != JsonValueKind.Array || scenes.GetArrayLength() is < 1 or > 1000)
            throw new InvalidDataException("工程没有有效场景。");
        foreach (var s in scenes.EnumerateArray())
        {
            if (s.TryGetProperty("nodes", out var nodes))
                foreach (var node in nodes.EnumerateArray())
                    if (node.TryGetProperty("source", out var source) && !manifest.AssetHashes.ContainsKey(source.GetString()!))
                        throw new InvalidDataException("场景引用了未登记的素材。");
        }
        if (manifest.VoiceFile is not null && manifest.TimestampsFile is null)
            throw new InvalidDataException("配音工程缺少字级时间戳，请重新制作。");
        if (manifest.SfxFile is not null)
        {
            var sounds = JsonSerializer.Deserialize<VibeSoundTrack>(await File.ReadAllTextAsync(ResolveAsset(root, manifest.SfxFile), ct), JsonOptions)
                ?? throw new InvalidDataException("音效时间表无效。");
            if (sounds.Version != 1 || sounds.Events is null || sounds.Events.Any(e=>e is null || string.IsNullOrWhiteSpace(e.Source)) || sounds.Events.Length > 512 || sounds.Events.Select(e => e.Source).Distinct().Count() > 32)
                throw new InvalidDataException("音效版本或数量不受支持。");
            foreach (var sound in sounds.Events)
                if (sound.TimeUs < 0 || sound.TimeUs >= manifest.DurationUs || !double.IsFinite(sound.Gain) || sound.Gain is < 0 or > 2 || !manifest.AssetHashes.ContainsKey(sound.Source))
                    throw new InvalidDataException("音效时刻、音量或素材引用无效。");
        }
        return new(root, manifest, scene.RootElement.Clone());
    }

    public static string ResolveAsset(string root, string relative)
    {
        if (string.IsNullOrWhiteSpace(relative) || Path.IsPathRooted(relative) || relative.Contains('\\') || relative.Contains(':') || relative.Contains('#') || relative.Contains('?') || relative.Split('/').Any(p => p is "" or "." or ".."))
            throw new InvalidDataException("工程素材路径无效。");
        var path = Path.GetFullPath(Path.Combine(root, relative));
        var prefix = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        if (!path.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("工程素材超出工程目录。");
        for (var current = path; current.Length >= prefix.Length; current = Path.GetDirectoryName(current)!)
            if ((File.Exists(current) || Directory.Exists(current)) && File.GetAttributes(current).HasFlag(FileAttributes.ReparsePoint))
                throw new InvalidDataException("工程不支持链接素材，请将原文件打包到工程目录。");
        return path;
    }

    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNamingPolicy = JsonNamingPolicy.CamelCase };
}
