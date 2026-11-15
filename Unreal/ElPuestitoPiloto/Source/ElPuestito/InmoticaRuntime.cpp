#include "InmoticaRuntime.h"
#include "PuestitoDoor.h"
#include "Sockets.h"
#include "SocketSubsystem.h"
#include "IPAddress.h"
#include "EngineUtils.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Components/LightComponent.h"
#include "Components/MeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"

static uint16 Word(const TArray<uint8>& B,int I){return (uint16(B[I])<<8)|B[I+1];}
static void Put(TArray<uint8>& B,uint16 V){B.Add(V>>8);B.Add(V&255);}
static int Zone(AActor* A){for(int I=1;I<=9;I++)if(A->ActorHasTag(FName(*FString::Printf(TEXT("InmoticaZone%d"),I))))return I;return 0;}
void UInmoticaRuntime::OnWorldBeginPlay(UWorld& W){
 Super::OnWorldBeginPlay(W);
 auto* SS=ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
 Listener=SS->CreateSocket(NAME_Stream,TEXT("ElPuestito Modbus local"),false);
 auto Addr=SS->CreateInternetAddr();bool Valid=false;Addr->SetIp(TEXT("127.0.0.1"),Valid);Addr->SetPort(15020);
 if(Listener){Listener->SetNonBlocking(true);Listening=Valid&&Listener->Bind(*Addr)&&Listener->Listen(4);}
 Status=Listening?TEXT("Simulacion local disponible"):TEXT("Puerto ocupado: cerra Godot u otro recorrido y reinicia Unreal");
 UE_LOG(LogTemp,Display,TEXT("PUESTItO_MODBUS %s"),*Status);
 OffMaterial=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/RestauranteCompleto/M_LuminariaApagada.M_LuminariaApagada"));
 for(TActorIterator<AActor> It(&W);It;++It){
  AActor* A=*It;int Z=Zone(A);
  if(Z){if(auto* L=A->FindComponentByClass<ULightComponent>())Lights.Add(L,TPair<int,float>(Z,L->Intensity));
   if(A->ActorHasTag(TEXT("InmoticaEmitter")))if(auto* M=A->FindComponentByClass<UMeshComponent>()){
    Emitters.Add(M,Z);TArray<UMaterialInterface*> Mats;for(int I=0;I<M->GetNumMaterials();I++){Mats.Add(M->GetMaterial(I));RetainedMaterials.Add(M->GetMaterial(I));}OriginalMaterials.Add(M,Mats);
   }
  }
  if(auto* T=A->FindComponentByClass<UTextRenderComponent>()){
   if(A->ActorHasTag(TEXT("MetricPPM")))PpmText=T;
   if(A->ActorHasTag(TEXT("MetricWeight")))WeightText=T;
   if(A->ActorHasTag(TEXT("MetricBio")))BioText=T;
  }
 }
 UE_LOG(LogTemp,Display,TEXT("PUESTItO_BINDINGS lights=%d emitters=%d ppm=%d weight=%d bio=%d"),Lights.Num(),Emitters.Num(),PpmText.IsValid(),WeightText.IsValid(),BioText.IsValid());
 ApplyVisuals();
}
void UInmoticaRuntime::Deinitialize(){
 auto* SS=ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
 for(auto& P:Peers){P.Socket->Close();SS->DestroySocket(P.Socket);}Peers.Empty();
 if(Listener){Listener->Close();SS->DestroySocket(Listener);Listener=nullptr;}Listening=false;
 Super::Deinitialize();
}
void UInmoticaRuntime::Command(int A,bool V){
 if(A<0||A>17)return;
 if(A==0){for(int I=0;I<=9;I++)Coils[I]=V;Coils[11]=Coils[12]=false;}
 else if(A<=12){Coils[A]=V;if(A==4)Coils[11]=false;if(A==5)Coils[12]=false;}
 else if(V){if(A==13||A==14)Pir[A-13]=10;else if(A==15||A==16){Bio=A-14;++BioSequence;}else if(A==17)Mass=15;}
 Coils[0]=true;for(int I=1;I<=9;I++)Coils[0]&=Coils[I];
 ApplyVisuals();
}
void UInmoticaRuntime::Reply(FModbusPeer& P,const TArray<uint8>& F){
 const uint8 Fn=F[7];TArray<uint8> R;int Error=0;
 if(F[6]!=1)return;
 if(Fn!=4&&Fn!=5)Error=1;
 else if(F.Num()!=12)Error=3;
 else if(Fn==4){
  int Start=Word(F,8),Count=Word(F,10);
  if(Count<1||Count>11||Start+Count>11)Error=2;
  else {uint16 Mask=0;for(int I=0;I<13;I++)if(Coils[I])Mask|=1<<I;
   uint16 Regs[11]={uint16(Ppm),uint16(Alarm),uint16((15+Mass)*100),uint16(Mass*100),uint16(Mass/15*100),uint16(Pir[0]>0),uint16(Pir[1]>0),uint16(Bio),0x5055,Mask,BioSequence};
   R.Add(4);R.Add(Count*2);for(int I=Start;I<Start+Count;I++)Put(R,Regs[I]);
  }
 }else{int A=Word(F,8),V=Word(F,10);if(A>17)Error=2;else if((V!=0&&V!=0xff00)||(A>=13&&V==0))Error=3;else{Command(A,V!=0);R.Append(F.GetData()+7,5);}}
 if(Error){R.Reset();R.Add(Fn|0x80);R.Add(Error);}
 Put(P.Out,Word(F,0));Put(P.Out,0);Put(P.Out,R.Num()+1);P.Out.Add(1);P.Out.Append(R);
}
void UInmoticaRuntime::NetworkTick(){
 if(!Listening)return;
 auto* SS=ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);bool Pending=false;
 while(Listener->HasPendingConnection(Pending)&&Pending){auto* S=Listener->Accept(TEXT("POS local"));if(!S)break;if(Peers.Num()>=4){S->Close();SS->DestroySocket(S);break;}S->SetNonBlocking(true);S->SetNoDelay(true);FModbusPeer P;P.Socket=S;P.Last=FPlatformTime::Seconds();Peers.Add(MoveTemp(P));}
 for(int I=Peers.Num()-1;I>=0;I--){auto& P=Peers[I];bool Bad=false;uint32 Available=0;
  if(P.Socket->HasPendingData(Available)){uint8 B[1024];int32 Read=0;if(P.Socket->Recv(B,FMath::Min(int(Available),1024),Read)&&Read>0){P.In.Append(B,Read);P.Last=FPlatformTime::Seconds();}}
  if(P.In.Num()>1024)Bad=true;
  while(!Bad&&P.In.Num()>=7){int N=Word(P.In,4);if(Word(P.In,2)!=0||N<2||N>254){Bad=true;break;}if(P.In.Num()<N+6)break;
   TArray<uint8> F;F.Append(P.In.GetData(),N+6);P.In.RemoveAt(0,N+6,EAllowShrinking::No);Reply(P,F);
  }
  if(P.Out.Num()>4096)Bad=true;
  if(!Bad&&!P.Out.IsEmpty()){int32 Sent=0;if(P.Socket->Send(P.Out.GetData(),P.Out.Num(),Sent)&&Sent>0)P.Out.RemoveAt(0,Sent,EAllowShrinking::No);}
  if(Bad||FPlatformTime::Seconds()-P.Last>8||P.Socket->GetConnectionState()==SCS_ConnectionError){P.Socket->Close();SS->DestroySocket(P.Socket);Peers.RemoveAt(I);}
 }
}
void UInmoticaRuntime::Tick(float Dt){
 if(!HasCalledBeginPlay())return;
 Dt=FMath::Min(Dt,0.25f);
 auto* PC=GetWorld()->GetFirstPlayerController();
 DoorPrompt.Empty();
 if(PC){
  if(!PC->bShowMouseCursor){
   FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
   FHitResult Hit;FCollisionQueryParams Query(SCENE_QUERY_STAT(DoorInteraction),false,PC->GetPawn());
   if(GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+View.Vector()*220,ECC_Visibility,Query)){
    if(auto* Door=Cast<APuestitoDoor>(Hit.GetActor())){
     if(PC->WasInputKeyJustPressed(EKeys::F))Door->Toggle();
     DoorPrompt=Door->Prompt();
    }
   }
  }
  if(!HudSet){PC->ClientSetHUD(APuestitoHUD::StaticClass());HudSet=true;}
  if(PC->WasInputKeyJustPressed(EKeys::F1))ShowHelp=!ShowHelp;
  if(PC->WasInputKeyJustPressed(EKeys::F2))Command(10,!Coils[10]);
  if(PC->WasInputKeyJustPressed(EKeys::F3))Command(0,!Coils[0]);
  if(PC->WasInputKeyJustPressed(EKeys::F4))Command(13,true);
  if(PC->WasInputKeyJustPressed(EKeys::F5))Command(14,true);
  if(PC->WasInputKeyJustPressed(EKeys::F6))Command(15,true);
  if(PC->WasInputKeyJustPressed(EKeys::F7))Command(16,true);
  if(PC->WasInputKeyJustPressed(EKeys::F8))Command(17,true);
  if(PC->WasInputKeyJustPressed(EKeys::Escape)){bool Show=!PC->bShowMouseCursor;PC->bShowMouseCursor=Show;if(Show)PC->SetInputMode(FInputModeGameAndUI());else PC->SetInputMode(FInputModeGameOnly());}
  if(APawn* Pawn=PC->GetPawn()){
   FVector V=Pawn->GetActorLocation();float X=V.X/100+4.8f,Z=V.Y/100+24.6f;
   if(X>6.55&&X<9.8&&V.Z<290){if(Z>15.8&&Z<18)Pir[0]=10;if(Z>13.5&&Z<15.65)Pir[1]=10;}
   FVector Reader(-28,-745,162);if(PC->WasInputKeyJustPressed(EKeys::R)&&FVector::Dist(V,Reader)<180)Command(15,true);
  }
 }
 for(int I=0;I<2;I++){Pir[I]=FMath::Max(0.f,Pir[I]-Dt);if(Coils[11+I])Coils[4+I]=Pir[I]>0;}
 Coils[0]=true;for(int I=1;I<=9;I++)Coils[0]&=Coils[I];
 Mass=FMath::Max(0.f,Mass-Dt*(Coils[10]?.055f:.005f));
 Ppm=FMath::FInterpConstantTo(Ppm,Coils[10]?2500.f:250.f,Dt,Coils[10]?100.f:50.f);
 if(Ppm>800)Alarm=2;else if(Alarm==2&&Ppm<700)Alarm=1;else if(Alarm==0&&Ppm>400)Alarm=1;else if(Alarm==1&&Ppm<350)Alarm=0;
 NetworkTick();VisualTime+=Dt;if(VisualTime>.2f){VisualTime=0;ApplyVisuals();}
}
void UInmoticaRuntime::ApplyVisuals(){
 for(auto& Entry:Lights)if(Entry.Key.IsValid())Entry.Key->SetIntensity(Coils[Entry.Value.Key]?Entry.Value.Value:0);
 for(auto& Entry:Emitters)if(Entry.Key.IsValid()&&OffMaterial){auto* M=Entry.Key.Get();auto* Mats=OriginalMaterials.Find(Entry.Key);if(Mats)for(int I=0;I<Mats->Num();I++)M->SetMaterial(I,Coils[Entry.Value]?(*Mats)[I]:OffMaterial.Get());}
 if(PpmText.IsValid()){PpmText->SetText(FText::FromString(FString::Printf(TEXT("%.0f ppm"),Ppm)));PpmText->SetTextRenderColor(Alarm==2?FColor::Red:Alarm==1?FColor::Orange:FColor::Cyan);}
 if(WeightText.IsValid())WeightText->SetText(FText::FromString(FString::Printf(TEXT("%.2f kg / %.0f%%"),15+Mass,Mass/15*100)));
 if(BioText.IsValid())BioText->SetText(FText::FromString(Bio==1?TEXT("ACEPTADA"):Bio==2?TEXT("NO RECONOCIDA"):TEXT("ACERCAR DEDO [R]")));
}
void APuestitoHUD::DrawHUD(){
 Super::DrawHUD();auto* S=GetWorld()->GetSubsystem<UInmoticaRuntime>();if(!Canvas||!S)return;
 const float Scale=FMath::Clamp(Canvas->ClipX/1280.f,.7f,1.3f);const float X=22,Y=20,W=365*Scale;
 DrawRect(FLinearColor(.015,.035,.045,.88),X,Y,W,160*Scale);
 auto Line=[&](const FString& T,int Row,FLinearColor C){DrawText(T,C,X+14*Scale,Y+(12+Row*24)*Scale,GEngine->GetSmallFont(),Scale*1.12f);};
 Line(TEXT("EL PUESTITO | SIMULACION"),0,FLinearColor(.4,1,.8));
 Line(FString::Printf(TEXT("Cocina: %.0f ppm | %s"),S->Ppm,S->Alarm==2?TEXT("ALARMA"):S->Alarm==1?TEXT("PREALERTA"):TEXT("NORMAL")),1,S->Alarm?FLinearColor(1,.45,.25):FLinearColor::White);
 Line(FString::Printf(TEXT("Gas: %.0f%% | Neto %.2f kg"),S->Mass/15*100,S->Mass),2,FLinearColor::White);
 Line(FString::Printf(TEXT("Banos: M %s / H %s"),S->Pir[0]>0?TEXT("ocupado"):TEXT("libre"),S->Pir[1]>0?TEXT("ocupado"):TEXT("libre")),3,FLinearColor::White);
 Line(S->Bio==1?TEXT("Biometria: aceptada"):S->Bio==2?TEXT("Biometria: rechazada"):TEXT("Biometria: sin lecturas"),4,FLinearColor::White);
 Line(S->Listening?TEXT("POS disponible | F1: ayuda"):TEXT("PUERTO OCUPADO - cerrar otro simulador"),5,S->Listening?FLinearColor(.6,.8,.85):FLinearColor(1,.3,.2));
 DrawRect(FLinearColor(.015,.035,.045,.8),X,Canvas->ClipY-46*Scale,Canvas->ClipX-2*X,32*Scale);
 DrawText(TEXT("WASD: recorrer | Raton: mirar | Q/E: altura | F: puerta | Esc: cursor | Alt+F4: salir"),FLinearColor::White,X+12,Canvas->ClipY-39*Scale,GEngine->GetSmallFont(),Scale);
 if(!PlayerOwner->bShowMouseCursor){DrawRect(FLinearColor(1,1,1,.8),Canvas->ClipX*.5f-2,Canvas->ClipY*.5f-2,4,4);}
 if(!S->DoorPrompt.IsEmpty()){
  const float PW=FMath::Min(620*Scale,Canvas->ClipX-44);
  DrawRect(FLinearColor(.015,.035,.045,.92),(Canvas->ClipX-PW)*.5f,Canvas->ClipY-94*Scale,PW,34*Scale);
  DrawText(S->DoorPrompt,FLinearColor(.7,1,.86),(Canvas->ClipX-PW)*.5f+12,Canvas->ClipY-86*Scale,GEngine->GetSmallFont(),Scale*1.05f);
 }
 if(S->ShowHelp){DrawRect(FLinearColor(.015,.035,.045,.94),X,Y+174*Scale,W,178*Scale);const TCHAR* Rows[]={TEXT("PRUEBAS DIDACTICAS / SIN EQUIPOS REALES"),TEXT("F2: fuga de gas | F3: todas las luces"),TEXT("F4/F5: presencia mujeres/hombres"),TEXT("F6/F7: biometria aceptada/rechazada"),TEXT("F8: sustituir cilindro"),TEXT("Luces independientes y automaticos: POS"),TEXT("R cerca del lector: identificar")};for(int I=0;I<7;I++)DrawText(Rows[I],FLinearColor::White,X+12,Y+(182+I*23)*Scale,GEngine->GetSmallFont(),Scale);}
}
