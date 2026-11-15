using UnrealBuildTool;
public class ElPuestito : ModuleRules {
 public ElPuestito(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","InputCore","Sockets","Networking"});
 }
}
