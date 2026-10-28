using System.Text.Json;
using System.Text.Json.Serialization;

namespace WeMediaForge.Application.Models.WebProcess;

[JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
public sealed record VibeProjectManifest
{
    public int SchemaVersion { get; init; }
    public string RuntimeVersion { get; init; } = "";
    public string RuntimeSha256 { get; init; } = "";
    public string Title { get; init; } = "";
    public int Width { get; init; }
    public int Height { get; init; }
    public long DurationUs { get; init; }
    public string HtmlFile { get; init; } = "";
    public string SceneFile { get; init; } = "";
    public string? VoiceFile { get; init; }
    public string? TimestampsFile { get; init; }
    public string? ScriptFile { get; init; }
    public string? SfxFile { get; init; }
    public Dictionary<string, string> AssetHashes { get; init; } = new(StringComparer.Ordinal);
}

public sealed record VibeProject(string Root, VibeProjectManifest Manifest, JsonElement Scene)
{
    public string HtmlPath => Path.Combine(Root, Manifest.HtmlFile);
    public string? VoicePath => Manifest.VoiceFile is null ? null : Path.Combine(Root, Manifest.VoiceFile);
    public string? SfxPath => Manifest.SfxFile is null ? null : Path.Combine(Root, Manifest.SfxFile);
}
