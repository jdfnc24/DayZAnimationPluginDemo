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
	class DZ_JDsAnimationDemo
	{
		name = "JDsAnimationDemo";
		dir = "JDsAnimationDemo";
		credits = "";
		author = "";
		type = "mod";
		dependencies[] =
		{
			"Game", "World", "Mission"
		};
		class defs
		{
			class imageSets
			{
				files[]= {};
			};
			class engineScriptModule
			{
				value = "";
				files[] =
				{
					"JDsAnimationDemo/Scripts/common",
					"JDsAnimationDemo/Scripts/1_core"
				};
			};

			class gameScriptModule
			{
				value="";
				files[] = 
				{
					"JDsAnimationDemo/Scripts/common",
					"JDsAnimationDemo/Scripts/3_Game"
				};
			};
			class worldScriptModule
			{
				value="";
				files[] = 
				{
					"JDsAnimationDemo/Scripts/common",
					"JDsAnimationDemo/Scripts/4_World"
				};
			};

			class missionScriptModule 
			{
				value="";
				files[] = 
				{
					"JDsAnimationDemo/Scripts/common",
					"JDsAnimationDemo/Scripts/5_Mission"
				};
			};
		};
	};
};
