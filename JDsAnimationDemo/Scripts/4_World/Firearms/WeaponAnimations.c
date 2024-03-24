modded class ModItemRegisterCallbacks
{
    override void RegisterFireArms( DayZPlayerType pType, DayzPlayerItemBehaviorCfg pBehavior )
    {
        super.RegisterFireArms( pType, pBehavior );
        

		pType.AddItemInHandsProfileIK("JD_SVD_Base", "JDsAnimationDemo/Animations/SVD/JD_Demo_SVD.asi", pBehavior, "JDsAnimationDemo/Animations/SVD/JD_SVD_IK.anm", "JDsAnimationDemo/Animations/SVD/w_JD_SVD_states.anm");		
		
		
	}   

	
};   