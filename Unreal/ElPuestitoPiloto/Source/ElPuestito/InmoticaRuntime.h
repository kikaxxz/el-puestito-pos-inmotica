#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "GameFramework/HUD.h"
#include "InmoticaRuntime.generated.h"
class FSocket;
struct FModbusPeer { FSocket* Socket=nullptr; TArray<uint8> In, Out; double Last=0; };
UCLASS()
class ELPUESTITO_API UInmoticaRuntime : public UTickableWorldSubsystem {
 GENERATED_BODY()
public:
 virtual void OnWorldBeginPlay(UWorld& World) override;
 virtual void Deinitialize() override;
 virtual void Tick(float Dt) override;
 virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UInmoticaRuntime,STATGROUP_Tickables); }
 virtual bool DoesSupportWorldType(EWorldType::Type Type) const override { return Type==EWorldType::Game || Type==EWorldType::PIE; }
 void Command(int Address,bool Value);
 bool Coils[13]={true,true,true,true,true,true,true,true,true,true,false,true,true};
 float Ppm=250, Mass=15, Pir[2]={0,0};
 int Alarm=0, Bio=0; uint16 BioSequence=0;
 bool Listening=false, ShowHelp=false;
 FString Status;
 FString DoorPrompt;
private:
 void NetworkTick();
 void ApplyVisuals();
 void Reply(FModbusPeer& Peer, const TArray<uint8>& Frame);
 FSocket* Listener=nullptr;
 TArray<FModbusPeer> Peers;
 float VisualTime=0;
 bool HudSet=false;
 TMap<TWeakObjectPtr<class ULightComponent>, TPair<int,float>> Lights;
 TMap<TWeakObjectPtr<class UMeshComponent>, int> Emitters;
 TMap<TWeakObjectPtr<class UMeshComponent>, TArray<class UMaterialInterface*>> OriginalMaterials;
 UPROPERTY() TObjectPtr<class UMaterialInterface> OffMaterial;
 UPROPERTY() TArray<TObjectPtr<class UMaterialInterface>> RetainedMaterials;
 TWeakObjectPtr<class UTextRenderComponent> PpmText, WeightText, BioText;
};
UCLASS()
class ELPUESTITO_API APuestitoHUD : public AHUD {
 GENERATED_BODY()
public: virtual void DrawHUD() override;
};
