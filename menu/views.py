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
                            0 as level
                        FROM menu_menu 
                        WHERE name = %s
    
                        UNION ALL
    
                        SELECT 
                            m.id,
                            m.name,
                            m.url,
                            m.parent_id,
                            mp.level + 1
                        FROM menu_menu m
                        INNER JOIN menu_path mp ON m.id = mp.parent_id
                    )
                    SELECT * FROM menu_path ORDER BY level DESC
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

        # menu_ids = [item['id'] for item in menu_chain]
        # menu_objects = Menu.objects.filter(id__in=menu_ids)
        #
        context = {
            'menu_objects': menu_chain,
            # 'menu_objects': menu_objects
        }

    else:
        menu = Menu.objects.filter(parent=None).prefetch_related('children')
        context = {'menu_objects': menu}
    return render(request, 'menu/main.html', context=context)
