modded class ModItemRegisterCallbacks
{
    override void RegisterFireArms( DayZPlayerType pType, DayzPlayerItemBehaviorCfg pBehavior )
    {
        super.RegisterFireArms( pType, pBehavior );
        

		pType.AddItemInHandsProfileIK("JD_SVD_Base", "JDsAnimationDemo/Animations/SVD/JD_Demo_SVD.asi", pBehavior, "JDsAnimationDemo/Animations/SVD/JD_SVD_IK.anm", "JDsAnimationDemo/Animations/SVD/w_JD_SVD_states.anm");		
		
		
	}   
	
	// override void CustomBoneRemapping(DayZPlayerType pType)
    // {
		// super.CustomBoneRemapping(pType);
		
		// pType.AddItemBoneRemap("JD_SVD_Base", { 
			// "bolt", 
			// "Weapon_Bolt", 
			// "magazine", 
			// "Weapon_Magazine", 
			// "trigger", 
			// "Weapon_Trigger", 
			// "charging", 
			// "Weapon_Bone_01", 
			// "bullet", 
			// "Weapon_Bullet", 
			// "mag_release", 
			// "Weapon_Bone_02", 
			// "boltrelease", 
			// "Weapon_Bone_03" 
		// });
		
	// }
	
};   