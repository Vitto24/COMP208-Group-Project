from django.shortcuts import render
from modules.models import Module
from grades.models import Grade

def grades(request):
    modules = Module.objects.all()
    
    # list of dictionaries to hold the module grades
    module_data = []
    for module in modules:
        # Grab only grades to that module
        module_grades = Grade.objects.filter(assignment__module=module)
        
        # Only add the module to the page if it has grades - commented out to make it easier to test
        #if module_grades.exists():
            
            #ready for weighted grade
        total_weighted_mark = 0
        
        for g in module_grades:
            # calculate the weighted mark for each grade, and add it to the total
            score = g.score or 0
            weight = (g.assignment.weight / 100) or 0

            total_weighted_mark += (score * weight)
        
        module_data.append({
            'module': module,
            'grades': module_grades,
            'overall_grade': round(total_weighted_mark, 1) # Added the result here
        })
    
    return render(request, 'grades/grades.html', {'module_data': module_data})