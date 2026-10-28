using System.Security.Cryptography;
using System.Text.Json;
using WeMediaForge.Application.Models.WebProcess;

namespace WeMediaForge.Application.Helpers;

/// <summary>Export requires an externally trusted approval; draft preview remains available.</summary>
public static class VibeReleaseVerifier
{
    public static async Task VerifyAsync(VibeProject project, CancellationToken ct = default)
    {
        ct.ThrowIfCancellationRequested();
        var configured = Environment.GetEnvironmentVariable("VIBE_TRUST_STORE");
        if (string.IsNullOrWhiteSpace(configured))
            throw new InvalidDataException("尚未配置独立审核签发方，工程可预览但不能正式导出。");
        var root = Path.GetFullPath(project.Root);
        var trustPath = Path.GetFullPath(configured);
        if (trustPath.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("审核信任配置必须由工程之外的受控环境管理。");
        if (project.Manifest.Width != 1080 || project.Manifest.Height != 1920)
            throw new InvalidDataException("正式知识视频必须使用 1080×1920 标准画幅。");
        using var trust = JsonDocument.Parse(await File.ReadAllTextAsync(trustPath, ct));
        using var envelope = JsonDocument.Parse(await File.ReadAllTextAsync(Asset(root,"release.attestation.json"),ct));
        var e = envelope.RootElement;
        if (e.EnumerateObject().Count()!=4 || e.GetProperty("version").GetInt32()!=1 || trust.RootElement.GetProperty("version").GetInt32()!=1)
            throw new InvalidDataException("不支持的审核凭证格式。");
        var id=e.GetProperty("keyId").GetString()!;
        var authority=trust.RootElement.GetProperty("keys").GetProperty(id);
        using var key=RSA.Create();key.ImportFromPem(authority.GetProperty("publicKeyPem").GetString()!);
        if (key.KeySize<3072 || Hex(SHA256.HashData(key.ExportSubjectPublicKeyInfo()))!=id)
            throw new InvalidDataException("审核公钥身份无效。");
        var payloadBytes=Convert.FromBase64String(e.GetProperty("payload").GetString()!);
        if (!key.VerifyData(payloadBytes,Convert.FromBase64String(e.GetProperty("signature").GetString()!),HashAlgorithmName.SHA256,RSASignaturePadding.Pss))
            throw new InvalidDataException("审核凭证签名无效。");
        using var payload=JsonDocument.Parse(payloadBytes);var p=payload.RootElement;
        var reviewer=authority.GetProperty("reviewerId").GetString();
        if (p.GetProperty("version").GetInt32()!=1 || p.GetProperty("status").GetString()!="approved" ||
            (p.GetProperty("profile").GetString() is not ("knowledge-portrait-v1" or "presentation-portrait-v1")) || p.GetProperty("reviewerId").GetString()!=reviewer)
            throw new InvalidDataException("审核凭证不适用于当前发布流程。");
        await CheckHash(root,"vibe.project.json",p.GetProperty("manifestSha256").GetString()!,ct);
        await CheckHash(root,"quality-plan.json",p.GetProperty("planSha256").GetString()!,ct);
        await CheckHash(root,"quality-review.json",p.GetProperty("reviewSha256").GetString()!,ct);
        using var plan=JsonDocument.Parse(await File.ReadAllTextAsync(Asset(root,"quality-plan.json"),ct));
        using var review=JsonDocument.Parse(await File.ReadAllTextAsync(Asset(root,"quality-review.json"),ct));
        if (plan.RootElement.GetProperty("profile").GetString()!=p.GetProperty("profile").GetString() ||
            plan.RootElement.GetProperty("authorId").GetString()==reviewer || review.RootElement.GetProperty("reviewer").GetString()!=reviewer ||
            review.RootElement.GetProperty("status").GetString()!="passed" ||
            review.RootElement.GetProperty("inputFingerprint").GetString()!=p.GetProperty("inputFingerprint").GetString() ||
            review.RootElement.GetProperty("evidenceDigest").GetString()!=p.GetProperty("evidenceDigest").GetString())
            throw new InvalidDataException("生成者与审核者未分离，或复核记录已过期。");
        await CheckHash(root,"quality-evidence/index.json",p.GetProperty("evidenceDigest").GetString()!,ct);
        using var index=JsonDocument.Parse(await File.ReadAllTextAsync(Asset(root,"quality-evidence/index.json"),ct));
        if (index.RootElement.GetArrayLength()==0)throw new InvalidDataException("审核截图证据为空。");
        foreach(var item in index.RootElement.EnumerateArray())
            await CheckHash(root,"quality-evidence/"+item.GetProperty("file").GetString(),item.GetProperty("sha256").GetString()!,ct);
    }

    private static string Asset(string root,string name)=>VibeProjectReader.ResolveAsset(root,name);
    private static string Hex(byte[] bytes)=>Convert.ToHexString(bytes).ToLowerInvariant();
    private static async Task CheckHash(string root,string name,string expected,CancellationToken ct)
    {
        await using var stream=File.OpenRead(Asset(root,name));
        if(Hex(await SHA256.HashDataAsync(stream,ct))!=expected)
            throw new InvalidDataException("发布包或证据已更改："+name);
    }
}
