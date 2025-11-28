from django.shortcuts import render
from django.db import connection
from .models import Menu

# Create your views here.
def menu_render(request, name=None):
    if name:
        with connection.cursor() as cur:
            cur.execute("""
                    WITH RECURSIVE menu_path AS (

                        SELECT 
                            id,
                            name,
                            url,
                            parent_id,
                            0 as level,
                            'current' as direction
                        FROM menu_menu 
                        WHERE name = %s
                    
                        UNION ALL
                    
                        SELECT 
                            m.id,
                            m.name,
                            m.url,
                            m.parent_id,
                            mp.level - 1,
                            'parent' as direction
                        FROM menu_menu m
                        INNER JOIN menu_path mp ON m.id = mp.parent_id
                        WHERE mp.direction IN ('current', 'parent')
                    
                        UNION ALL
                    
                        SELECT 
                            m.id,
                            m.name,
                            m.url,
                            m.parent_id,
                            mp.level + 1,
                            'child' as direction
                        FROM menu_menu m
                        INNER JOIN menu_path mp ON m.parent_id = mp.id
                        WHERE mp.direction = 'current'
                    )
                    SELECT DISTINCT * FROM menu_path 
                    ORDER BY 
                        level ASC; 
                """, [name])

            result = cur.fetchall()
        menu_chain = []
        for row in result:
            menu_chain.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'parent_id': row[3],
                'level': row[4]
            })
        parents = [obj for obj in menu_chain if obj['level'] < 0]
        current = [obj for obj in menu_chain if obj['level'] == 0]
        children = [obj for obj in menu_chain if obj['level'] > 0]
        context = {
            "menu_objects": {"parents": parents, "current": current, "children": children}
        }

    else:
        menu = Menu.objects.filter(parent=None).prefetch_related('children')

        context = {"menu_objects": {"parents": None, "current": menu, "children": None}}

    return render(request, 'menu/main.html', context=context)
