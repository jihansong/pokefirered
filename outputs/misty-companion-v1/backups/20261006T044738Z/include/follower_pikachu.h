#ifndef GUARD_FOLLOWER_PIKACHU_H
#define GUARD_FOLLOWER_PIKACHU_H

extern bool8 gIgnoreFollowerPikachuCollision;

struct ObjectEvent *GetFollowerPikachuObject(void);
bool8 IsFollowerPikachuObject(struct ObjectEvent *objectEvent);
bool8 ShouldIgnoreCollisionWithFollower(struct ObjectEvent *mover, struct ObjectEvent *other);
void FollowerPikachu_OnMapLoad(void);
void FollowerPikachu_Update(void);
void FollowerPikachu_OnPlayerMovement(u8 movementActionId);
void FollowerPikachu_OnObjectMovement(struct ObjectEvent *objectEvent, u8 movementActionId);
void Task_FollowerPikachu(u8 taskId);
void CreateFollowerPikachuTask(void);
void HideFollowerPikachu(void);
void ShowFollowerPikachu(void);

#endif // GUARD_FOLLOWER_PIKACHU_H
