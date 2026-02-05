from departments.models import Department
import urllib.request
codes=[c[0] for c in Department.DEPARTMENT_CHOICES]
base='http://127.0.0.1:8000'
for code in codes:
    u=f"{base}/departments/{code}/"
    try:
        r=urllib.request.urlopen(u, timeout=10)
        print(code, r.getcode())
    except Exception as e:
        print(code, 'ERROR', e)
