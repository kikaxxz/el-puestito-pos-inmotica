using UnrealBuildTool;
public class ElPuestitoPilotoTarget : TargetRules {
 public ElPuestitoPilotoTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Game; DefaultBuildSettings = BuildSettingsVersion.V7;
  IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
  ExtraModuleNames.Add("ElPuestito");
 }
}
