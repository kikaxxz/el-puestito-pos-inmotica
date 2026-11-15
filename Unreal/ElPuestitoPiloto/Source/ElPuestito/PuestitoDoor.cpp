#include "PuestitoDoor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "HAL/IConsoleManager.h"

APuestitoDoor::APuestitoDoor(){
 PrimaryActorTick.bCanEverTick=true;
 Hinge=CreateDefaultSubobject<USceneComponent>(TEXT("Bisagra"));SetRootComponent(Hinge);Hinge->SetMobility(EComponentMobility::Movable);
 Leaf=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hoja"));Leaf->SetupAttachment(Hinge);Leaf->SetMobility(EComponentMobility::Movable);Leaf->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Handle=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Manilla"));Handle->SetupAttachment(Hinge);Handle->SetMobility(EComponentMobility::Movable);Handle->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Blocker=CreateDefaultSubobject<UBoxComponent>(TEXT("ColisionHoja"));Blocker->SetupAttachment(Hinge);Blocker->SetMobility(EComponentMobility::Movable);
 Blocker->SetCollisionProfileName(TEXT("BlockAllDynamic"));Blocker->SetGenerateOverlapEvents(false);Blocker->SetCanEverAffectNavigation(false);
}
void APuestitoDoor::ConfigureCollision(){
 if(!Leaf->GetStaticMesh())return;
 const FBox B=Leaf->GetStaticMesh()->GetBoundingBox();
 Blocker->SetRelativeLocation(B.GetCenter());Blocker->SetBoxExtent(B.GetExtent().ComponentMax(FVector(1.2)),true);
}
void APuestitoDoor::BeginPlay(){Super::BeginPlay();ConfigureCollision();SetActorRotation(FRotator::ZeroRotator);CurrentAngle=0;}
bool APuestitoDoor::IsAngleClear(float Angle){
 LastObstacle.Empty();if(!GetWorld()||!Leaf->GetStaticMesh())return false;
 const FQuat Q=FRotator(0,Angle,0).Quaternion();
 FVector Offset=Blocker->GetRelativeLocation();
 const FVector FullExtent=Blocker->GetUnscaledBoxExtent();
 // The first 6 cm sit in the hinge fitting; test the moving panel beyond that fitting.
 const bool AlongX=FullExtent.X>FullExtent.Y;
 if(AlongX)Offset.X+=3;else Offset.Y+=3;
 const FVector C=GetActorLocation()+Q.RotateVector(Offset);
 // Leave a small fitting tolerance at the frame, but test almost the entire leaf.
 FVector Extent=(FullExtent-FVector(2,2,2)).ComponentMax(FVector(.6));
 if(AlongX)Extent.X-=3;else Extent.Y-=3;
 FCollisionQueryParams Params(SCENE_QUERY_STAT(PuestitoDoorClearance),false,this);
 FCollisionObjectQueryParams Objects;Objects.AddObjectTypesToQuery(ECC_WorldStatic);Objects.AddObjectTypesToQuery(ECC_WorldDynamic);Objects.AddObjectTypesToQuery(ECC_Pawn);
 TArray<FOverlapResult> Hits;
 GetWorld()->OverlapMultiByObjectType(Hits,C,Q,Objects,FCollisionShape::MakeBox(Extent),Params);
 for(const FOverlapResult& Hit:Hits){
  const UPrimitiveComponent* Component=Hit.GetComponent();
  if(Component&&Component->GetCollisionResponseToChannel(ECC_Pawn)==ECR_Block){
   LastObstacle=Hit.GetActor()?Hit.GetActor()->GetName():TEXT("obstaculo");return false;
  }
 }
 return true;
}
void APuestitoDoor::Toggle(){
 bTargetOpen=!bTargetOpen;StartAngle=CurrentAngle;Elapsed=0;bMoving=true;bBlocked=false;
}
void APuestitoDoor::Tick(float Dt){
 Super::Tick(Dt);if(!bMoving)return;
 Elapsed+=FMath::Min(Dt,.05f);
 const float T=FMath::Clamp(Elapsed/.85f,0.f,1.f);
 const float Target=bTargetOpen?OpenYaw:0.f;
 const float Next=FMath::Lerp(StartAngle,Target,T*T*(3-2*T));
 // Rotation sweeps are not supported by SetActorRotation: explicitly sample the arc.
 const int Steps=FMath::Max(1,FMath::CeilToInt(FMath::Abs(Next-CurrentAngle)/.75f));
 const float From=CurrentAngle;
 for(int I=1;I<=Steps;I++){
  const float Candidate=FMath::Lerp(From,Next,float(I)/Steps);
  if(!IsAngleClear(Candidate)){bBlocked=true;bMoving=false;UE_LOG(LogTemp,Display,TEXT("DOOR_BLOCKED %s angle=%.2f obstacle=%s"),*DoorTitle,CurrentAngle,*LastObstacle);return;}
  CurrentAngle=Candidate;SetActorRotation(FRotator(0,CurrentAngle,0));
 }
 if(T>=1)bMoving=false;
}
FString APuestitoDoor::Prompt() const{
 return FString::Printf(TEXT("[F] %s - %s%s"),bTargetOpen?TEXT("Cerrar"):TEXT("Abrir"),*DoorTitle,bBlocked?TEXT(" | Paso ocupado"):TEXT(""));
}

#if !UE_BUILD_SHIPPING
// Deterministic packaged-runtime check of complete arcs and a player in the path.
static FAutoConsoleCommandWithWorld DoorTest(TEXT("puestito.TestDoors"),TEXT("Validate doors in the loaded map"),FConsoleCommandWithWorldDelegate::CreateLambda([](UWorld* World){
 if(!World)return;auto* PC=World->GetFirstPlayerController();APawn* Pawn=PC?PC->GetPawn():nullptr;
 FVector Saved=Pawn?Pawn->GetActorLocation():FVector::ZeroVector;if(Pawn)Pawn->SetActorLocation(FVector(-10000,-10000,500),false);
 int Total=0,Passed=0;
 for(TActorIterator<APuestitoDoor> It(World);It;++It){
  APuestitoDoor* D=*It;Total++;
  D->CurrentAngle=0;D->bTargetOpen=false;D->SetActorRotation(FRotator::ZeroRotator);D->Toggle();for(int N=0;N<70;N++)D->Tick(1.f/60);
  bool Open=FMath::IsNearlyEqual(D->CurrentAngle,D->OpenYaw,.1f);
  D->Toggle();for(int N=0;N<70;N++)D->Tick(1.f/60);
  bool Closed=FMath::IsNearlyZero(D->CurrentAngle,.1f);
  bool Stops=true;
  if(Pawn){
   const FQuat Q=FRotator(0,D->OpenYaw*.5f,0).Quaternion();
   FVector P=D->GetActorLocation()+Q.RotateVector(D->Blocker->GetRelativeLocation());P.Z=D->GetActorLocation().Z+140;
   Pawn->SetActorLocation(P,false);D->Toggle();for(int N=0;N<70;N++)D->Tick(1.f/60);
   Stops=D->bBlocked&&FMath::Abs(D->CurrentAngle)<FMath::Abs(D->OpenYaw);
   Pawn->SetActorLocation(FVector(-10000,-10000,500),false);D->Toggle();for(int N=0;N<70;N++)D->Tick(1.f/60);
  }
  if(Open&&Closed&&Stops)Passed++;
  UE_LOG(LogTemp,Display,TEXT("DOOR_TEST %s open=%d closed=%d player_stop=%d"),*D->DoorTitle,Open,Closed,Stops);
 }
 if(Pawn)Pawn->SetActorLocation(Saved,false);
 UE_LOG(LogTemp,Display,TEXT("DOOR_TEST_RESULT %d/%d"),Passed,Total);
}));
#endif
