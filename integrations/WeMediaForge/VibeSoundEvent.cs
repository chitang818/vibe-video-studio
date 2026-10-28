using System.Text.Json.Serialization;

namespace WeMediaForge.Application.Models.WebProcess;

[JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
public sealed record VibeSoundEvent
{
    public long TimeUs { get; init; }
    public string Source { get; init; } = "";
    public double Gain { get; init; } = 1;
}
[JsonUnmappedMemberHandling(JsonUnmappedMemberHandling.Disallow)]
public sealed record VibeSoundTrack
{
    public int Version { get; init; }
    public VibeSoundEvent[] Events { get; init; } = [];
}
