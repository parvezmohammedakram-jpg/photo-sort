import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models.project import Project
from app.models.photo import Photo
from app.models.analysis import Analysis, DuplicateGroup
from app.models.review import ManualReview
from app.services.pipeline import run_analysis_pipeline

if __name__ == '__main__':
    db = SessionLocal()
    p = db.query(Project).get(5)
    if p:
        p.status = 'pending'
        db.commit()
        print("Project reset to pending.")
    db.close()
    
    run_analysis_pipeline(5)
    print("Pipeline triggered.")
