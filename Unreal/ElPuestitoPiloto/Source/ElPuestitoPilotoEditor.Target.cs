using UnrealBuildTool;
public class ElPuestitoPilotoEditorTarget : TargetRules {
 public ElPuestitoPilotoEditorTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Editor; DefaultBuildSettings = BuildSettingsVersion.V7;
  IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
  ExtraModuleNames.Add("ElPuestito");
 }
}
