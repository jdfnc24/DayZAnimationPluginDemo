class CfgPatches
{
	class JDsAnimationDemo_Scripts
	{
		requiredAddons[] = { "DZ_Scripts" };
	};
};

class CfgAddons
{
    class PreloadAddons
    {
        class JDsAnimationDemo
        {
            list[]={};
        };
    };
};

class CfgMods
{
    class JDsAnimationDemo
    {
        name="";
        dir="JDsAnimationDemo";
        picture="";
        action="";
        author="";
        overview = "";
		inputs = "";
        defines[] = {};

        class defs
		{
			class imageSets
			{
				files[]= {};
			};
			class widgetStyles
			{
				files[]= {};
			};

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
