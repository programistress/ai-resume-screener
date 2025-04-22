TECHNICAL_SKILLS = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "C++", "C#", "Ruby", "Go", "PHP", "Swift", "Kotlin",
        "TypeScript", "Rust", "Scala", "R", "Perl", "Shell", "MATLAB", "SQL", "Lua"
    ],
    "frameworks": [
        "React", "Angular", "Vue", "Svelte", "Next.js", "Nuxt.js", "Django", "Flask", "FastAPI",
        "Spring", "Express", "NestJS", "Laravel", "Ruby on Rails", "ASP.NET Core",
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "OpenCV", "Hugging Face Transformers"
    ],
    "tools": [
        "Git", "GitHub", "GitLab", "Docker", "Kubernetes", "Jenkins", "CircleCI", "TravisCI",
        "JIRA", "Confluence", "Postman", "Insomnia", "Swagger", "Notion",
        "AWS", "Azure", "GCP", "Firebase", "Netlify", "Vercel", "Heroku",
        "VS Code", "IntelliJ IDEA", "PyCharm", "Eclipse", "Xcode",
        "Photoshop", "Figma", "Sketch", "Illustrator", "Canva"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Oracle"
    ],
    "devops": [
        "CI/CD", "Infrastructure as Code (IaC)", "Terraform", "Ansible", "Prometheus", "Grafana",
        "New Relic", "ELK Stack", "Logstash", "Splunk"
    ],
    "testing": [
        "JUnit", "Selenium", "Cypress", "Mocha", "Jest", "Pytest", "TestNG", "Postman Tests"
    ],
    "mobile_development": [
        "Flutter", "React Native", "SwiftUI", "Xamarin", "Ionic"
    ],
    "data_and_ai": [
        "Data analysis", "Data visualization", "Natural Language Processing (NLP)",
        "Machine Learning", "Deep Learning", "Model deployment", "ETL Pipelines",
        "Big Data", "Apache Spark", "Kafka", "Hadoop"
    ],
    "cybersecurity": [
        "OWASP Top 10", "Penetration Testing", "Threat Modeling", "SIEM", "IDS/IPS",
        "Network Security", "Vulnerability Scanning", "Firewalls", "Security Auditing"
    ],
    "other": [
        "Agile/Scrum", "Kanban", "Design Thinking", "UI/UX Principles", "Accessibility (a11y)",
        "SEO Optimization", "Content Management Systems (CMS)", "WordPress", "Drupal", "Shopify"
    ]
}

SOFT_SKILLS = {
    "communication": [
        "Public speaking", "Writing", "Presentation", "Active listening", "Clear communication",
        "Technical writing", "Documentation", "Stakeholder communication", "Interpersonal communication",
        "Email etiquette", "Giving and receiving feedback"
    ],
    "leadership": [
        "Team management", "Mentoring", "Coaching", "Decision making", "Strategic thinking",
        "Conflict resolution", "Project leadership", "Vision setting", "Delegation", "Change management"
    ],
    "problem_solving": [
        "Critical thinking", "Analytical skills", "Root cause analysis", "Troubleshooting",
        "Innovation", "Solution-focused thinking", "Creative problem solving"
    ],
    "collaboration": [
        "Teamwork", "Cross-functional collaboration", "Remote collaboration", "Empathy", 
        "Building rapport", "Peer learning", "Pair programming"
    ],
    "adaptability": [
        "Time management", "Stress management", "Resilience", "Open-mindedness",
        "Learning from feedback", "Work under pressure", "Flexibility"
    ],
    "organization": [
        "Goal setting", "Prioritization", "Task management", "Multitasking",
        "Attention to detail", "Meeting deadlines", "Planning and scheduling"
    ],
    "growth_mindset": [
        "Continuous learning", "Curiosity", "Self-awareness", "Receptiveness to feedback",
        "Initiative", "Motivation", "Persistence", "Accountability"
    ],
    "ethics_and_professionalism": [
        "Integrity", "Reliability", "Work ethic", "Respect", "Cultural sensitivity",
        "Confidentiality", "Inclusiveness"
    ]
}

# Combined dictionary for easier lookups
ALL_SKILLS = {}
for category, skills_dict in [("technical", TECHNICAL_SKILLS), ("soft", SOFT_SKILLS)]:
    for subcategory, skills_list in skills_dict.items():
        for skill in skills_list:
            ALL_SKILLS[skill.lower()] = {
                "category": category,
                "subcategory": subcategory,
                "name": skill
            }