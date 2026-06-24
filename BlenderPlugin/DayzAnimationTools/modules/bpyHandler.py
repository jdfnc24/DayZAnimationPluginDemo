import bpy
def registerClasses(classes):
    for cls in classes:
        bpy.utils.register_class(cls)

def registerMenus(menus, menuClass):
    for menu in menus:
        getattr(bpy.types, menuClass).append(menu)

def unregisterClasses(classes):
    for cls in classes:
        bpy.utils.unregister_class(cls)

def unregisterMenus(menus, menuClass):
    for menu in menus:
        getattr(bpy.types, menuClass).remove(menu)

def getOperator(context):
    sfile = context.space_data
    operator = sfile.active_operator
    return operator

def setLayoutProps(layout, operator, propsArray):
    for props in propsArray:
        layout.prop(operator, props)

def getLayout(self):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False
    return layout