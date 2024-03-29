class CfgPatches
{
	class JDsAnimationDemo_Scripts
	{
		requiredVersion = 0.1;
		requiredAddons[] = { "DZ_Scripts" };
	};
};

class CfgMods
{
    class JDsAnimationDemo
    {
        name="JDs Animation Demo";
        dir="JDsAnimationDemo";
        picture="";
        action="";
        author="jdfnc24";
        overview = "";
		inputs = "";
        defines[] = {};
		dependencies[] =
		{
			"Game", "World", "Mission"
		};
        class defs
		{

			class engineScriptModule 
			{ 
				files[] = { "JDsAnimationDemo/Scripts/1_Core"};
			};

			class gameScriptModule
			{
				files[] = { "JDsAnimationDemo/Scripts/3_Game" };
			};
			class worldScriptModule
			{
				files[] = { "JDsAnimationDemo/Scripts/4_World" };
			};

			class missionScriptModule 
			{
				files[] = { "JDsAnimationDemo/Scripts/5_Mission" };
			};
		};
    };
};
