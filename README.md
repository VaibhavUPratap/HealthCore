# **Smart Community Health Monitoring and Early Warning System for Water-Borne Diseases in Rural Northeast India**

This problem statement proposes the development of a Smart Health Surveillance and Early Warning System that can detect, monitor, and help prevent outbreaks of water-borne diseases in vulnerable communities. The system can be:

• Collect health data from local clinics, ASHA workers, and community volunteers via mobile apps or SMS.
• Use AI/ML models to detect patterns and predict potential outbreaks based on symptoms, water quality reports, and seasonal trends.
• Integrate with water testing kits or IoT sensors to monitor water source contamination (e.g., turbidity, pH, bacterial presence).
• Provide real-time alerts to district health officials and local governance bodies.
• Include a multilingual mobile interface for community reporting and awareness campaigns.
• Offer dashboards for health departments to visualize hotspots, track interventions, and allocate resources.

**Background**

Water-borne diseases such as diarrhea, cholera, typhoid, and hepatitis A are prevalent in many rural areas and tribal belts of the Northeastern Region (NER), especially during the monsoon season. These outbreaks are often linked to contaminated water sources, poor sanitation infrastructure, and delayed medical response. The terrain and remoteness of many villages make it difficult for health workers to monitor and respond to emerging health threats in time.

**Expected Solution**

A digital health platform that includes:

• A mobile app for data collection and community health reporting.
• AI-based outbreak prediction engine using health and environmental data.
• Integration with low-cost water quality sensors or manual test kits.
• Alert system for health authorities and local leaders.
• Educational modules for hygiene awareness and disease prevention.
• Offline functionality and support for tribal languages.

---

## Database Migration Notice

**⚠️ Important: Database has been migrated from MongoDB to SQLite**

Due to MongoDB connection issues, this project now uses SQLite as its database backend. SQLite is a lightweight, serverless database that requires no separate installation or configuration.

### What Changed:
- **Previous:** MongoDB (required separate MongoDB server installation)
- **Current:** SQLite (built-in, file-based database)
- Database file: `healthcore.db` (auto-created in project root)

### Benefits:
- ✅ No external database server needed
- ✅ Zero configuration required
- ✅ Portable and lightweight
- ✅ Perfect for development and small deployments
- ✅ Same API interface maintained for compatibility

### Configuration:
The database path is configurable via `.env`:
```
SQLITE_DB_PATH=healthcore.db
```

All existing database operations work the same way - the migration is transparent to the application code!
