using System.Security.Cryptography;
using WeMediaForge.Application.Helpers;

try
{
    VibeRuntimeIdentity.Sha256=Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(args[1]))).ToLowerInvariant();
    var project=await VibeProjectReader.LoadAsync(args[0]);
    await VibeReleaseVerifier.VerifyAsync(project);
    Console.WriteLine("consumer release accepted");
    return 0;
}
catch(Exception e)
{
    Console.WriteLine("consumer release rejected: "+e.GetType().Name);
    return 1;
}

namespace WeMediaForge.Application.Helpers
{
    public static class VibeRuntimeIdentity { public static string Sha256 {get;set;}=""; }
}
