#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PuestitoDoor.generated.h"

UCLASS()
class ELPUESTITO_API APuestitoDoor : public AActor {
 GENERATED_BODY()
public:
 APuestitoDoor();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaTime) override;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class USceneComponent> Hinge;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UStaticMeshComponent> Leaf;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UStaticMeshComponent> Handle;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UBoxComponent> Blocker;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) float OpenYaw=90;
 UPROPERTY(EditAnywhere, BlueprintReadWrite) FString DoorTitle;
 UFUNCTION(BlueprintCallable) void ConfigureCollision();
 UFUNCTION(BlueprintCallable) bool IsAngleClear(float Angle);
 void Toggle();
 FString Prompt() const;
 float CurrentAngle=0;
 bool bTargetOpen=false, bMoving=false, bBlocked=false;
 FString LastObstacle;
private:
 float StartAngle=0, Elapsed=0;
};
