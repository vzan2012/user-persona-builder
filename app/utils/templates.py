BASIC_TEMPLATE = """
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-basic {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; }}
                        .persona-header {{ text-align: center; margin-bottom: 15px; }}
                        .persona-header h2 {{ margin-bottom: 5px; color: #333; }}
                        .persona-header .subtitle {{ color: #777; font-size: 0.9em; }}
                        .persona-section {{ margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }}
                        .persona-section:last-child {{ border-bottom: none; }}
                        .persona-section h3 {{ color: #555; margin-top: 0; margin-bottom: 10px; }}
                        .persona-section p {{ margin-bottom: 5px; color: #444; }}
                        .persona-section p strong {{ font-weight: bold; color: #333; margin-right: 5px; }}
                        .user-photo {{ text-align: center; margin-bottom: 10px; }}
                        .user-photo img {{ width: 100px; height: auto; border-radius: 50%; object-fit: cover; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-basic">
                        <div class="user-photo">{image_html}</div>
                        <div class="persona-header">
                            <h2>{name}</h2>
                            <p class="subtitle">{occupation} • {location} • {age} years</p>
                        </div>
                        <div class="persona-section">
                            <h3>📌 Basic Information</h3>
                            <p><strong>Gender:</strong> {gender}</p>
                            <p><strong>Tech Savviness:</strong>'⭐' {tech_savviness}</p>
                        </div>
                        <div class="persona-section">
                            <h3>🎯 Goals & Motivations</h3>
                            <p><strong>Goals:</strong> {goals}</p>
                            <p><strong>Motivations:</strong> {motivations}</p>
                        </div>
                        <div class="persona-section">
                            <h3>⚠️ Pain Points</h3>
                            <p><strong>Frustrations:</strong> {frustrations}</p>
                            <p><strong>Challenges:</strong> {pain_points}</p>
                        </div>
                        <div class="persona-section">
                            <h3>🛠 Skills & Needs</h3>
                            <p><strong>Skills:</strong> {skills}</p>
                            <p><strong>Needs:</strong> {needs}</p>
                        </div>
                        <div class="persona-section">
                            <h3>🌐 Preferences</h3>
                            <p><strong>Interests:</strong> {', '.join({interests} or [])}</p>
                            <p><strong>Platforms:</strong> {', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()

MODERN_TEMPLATE = """
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-modern-stacked {{ background-color: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); padding: 25px; }}
                        .user-photo-modern-stacked img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin: 0 auto 15px auto; display: block; }}
                        .modern-header {{ text-align: center; margin-bottom: 20px; }}
                        .modern-header h2 {{ color: #2c3e50; margin-bottom: 8px; }}
                        .modern-header .subtitle {{ color: #777; font-size: 0.9em; margin-bottom: 5px; }}
                        .modern-header .tech-savvy {{ color: #3498db; font-size: 0.95em; }}
                        .modern-section {{ margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid #eee; }}
                        .modern-section:last-child {{ border-bottom: none; }}
                        .modern-section h3 {{ color: #2c3e50; margin-top: 0; margin-bottom: 10px; font-size: 1.15em; }}
                        .modern-section p {{ color: #555; margin-bottom: 0; font-size: 0.95em; line-height: 1.6; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-modern-stacked">
                        <div class="user-photo-modern-stacked">{image_html}</div>
                        <div class="modern-header">
                            <h2>{persona_data.get('name', '')}</h2>
                            <p class="subtitle">{persona_data.get('occupation', '')} • {persona_data.get('location', '')} • {persona_data.get('age', '')} years</p>
                            <div class="tech-savvy"><strong>Tech Savviness:</strong> {'⭐' * persona_data.get('tech_savviness', 0)}</div>
                        </div>
                        <div class="modern-section">
                            <h3>🎯 Goals</h3>
                            <p>{persona_data.get('goals', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>💡 Motivations</h3>
                            <p>{persona_data.get('motivations', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>⚠️ Frustrations</h3>
                            <p>{persona_data.get('frustrations', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>💔 Pain Points</h3>
                            <p>{persona_data.get('pain_points', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>🛠 Skills</h3>
                            <p>{persona_data.get('skills', '')}</p>
                        </div>
                        <div class="modern-section">
                            <h3>🌐 Interests</h3>
                            <p>{', '.join(persona_data.get('interests', []) or [])}</p>
                        </div>
                        <div class="modern-section">
                            <h3>📱 Platforms</h3>
                            <p>{', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                        <div class="modern-section">
                            <h3>👤 Gender</h3>
                            <p>{persona_data.get('gender', '')}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()

PROFESSIONAL_TEMPLATE = """
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-professional {{ border: 1px solid #aaa; padding: 20px; border-radius: 3px; background-color: #f0f0f0; }}
                        .professional-header {{ text-align: center; margin-bottom: 20px; }}
                        .user-photo-professional img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 15px; }}
                        .professional-header h2 {{ color: #222; margin-bottom: 5px; }}
                        .professional-header .title {{ color: #555; font-size: 1em; margin-bottom: 3px; }}
                        .professional-header .location {{ color: #777; font-size: 0.9em; }}
                        .professional-section {{ margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid #ccc; }}
                        .professional-section:last-child {{ border-bottom: none; }}
                        .professional-section h3 {{ color: #333; margin-top: 0; margin-bottom: 10px; font-size: 1.2em; border-bottom: 2px solid #555; padding-bottom: 5px; display: flex; align-items: center; gap: 8px; }}
                        .professional-section p {{ margin-bottom: 8px; color: #444; line-height: 1.5; display: flex; align-items: center; gap: 8px; }}
                        .professional-section p strong {{ font-weight: bold; color: #222; margin-right: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-professional">
                        <div class="professional-header">
                            <div class="user-photo-professional">{image_html}</div>
                            <h2>{persona_data.get('name', '')}</h2>
                            <p class="title">{persona_data.get('occupation', '')}</p>
                            <p class="location">📍 {persona_data.get('location', '')} | 🗓️ Age: {persona_data.get('age', '')}</p>
                        </div>
                        <div class="professional-section">
                            <h3>👤 About</h3>
                            <p><strong>Gender:</strong> {persona_data.get('gender', '')}</p>
                            <p><strong>💻 Tech Savviness:</strong> Level {persona_data.get('tech_savviness', 0)}</p>
                        </div>
                        <div class="professional-section">
                            <h3>💼 Professional Profile</h3>
                            <p><strong>🎯 Goals:</strong> {persona_data.get('goals', '')}</p>
                            <p><strong>🚀 Motivations:</strong> {persona_data.get('motivations', '')}</p>
                            <p><strong> skills:</strong> {persona_data.get('skills', '')}</p>
                        </div>
                        <div class="professional-section">
                            <h3>⚠️ Challenges & Needs</h3>
                            <p><strong>😠 Frustrations:</strong> {persona_data.get('frustrations', '')}</p>
                            <p><strong>💔 Pain Points:</strong> {persona_data.get('pain_points', '')}</p>
                            <p><strong>✅ Needs:</strong> {persona_data.get('needs', '')}</p>
                        </div>
                        <div class="professional-section">
                            <h3>🌐 Preferences</h3>
                            <p><strong>❤️ Interests:</strong> {', '.join(persona_data.get('interests', []) or [])}</p>
                            <p><strong>📱 Platforms:</strong> {', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()

CREATIVE_TEMPLATE = """
                <html>
                <head>
                    <style>
                        body {{ font-family: sans-serif; }}
                        .persona-card-creative {{ background-color: #e0f7fa; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08); border: 2px solid #b2ebf2; }}
                        .creative-header {{ text-align: center; margin-bottom: 25px; }}
                        .user-photo-creative img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 15px; }}
                        .creative-header h1 {{ color: #00838f; margin-bottom: 5px; font-size: 2.5em; }}
                        .creative-header .tagline {{ color: #26a69a; font-size: 1.1em; }}
                        .creative-section {{ margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px dashed #80cbc4; }}
                        .creative-section:last-child {{ border-bottom: none; }}
                        .creative-section h2 {{ color: #00acc1; margin-top: 0; margin-bottom: 12px; font-size: 1.8em; display: flex; align-items: center; gap: 8px; }}
                        .creative-section p {{ margin-bottom: 10px; color: #333; line-height: 1.6; display: flex; align-items: center; gap: 8px; }}
                        .creative-section p strong {{ font-weight: bold; color: #00695c; margin-right: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="persona-card-creative">
                        <div class="creative-header">
                            <div class="user-photo-creative">{image_html}</div>
                            <h1>✨ {persona_data.get('name', '')} ✨</h1>
                            <p class="tagline">💼 {persona_data.get('occupation', '')} | 🗓️ {persona_data.get('age', '')} | 📍 {persona_data.get('location', '')}</p>
                        </div>
                        <div class="creative-section">
                            <h2>🌍 My World</h2>
                            <p><strong>👤 Gender:</strong> {persona_data.get('gender', '')}</p>
                            <p><strong>💻 Tech Level:</strong> {persona_data.get('tech_savviness', 0)}/5</p>
                            <p><strong>❤️ Passions:</strong> {', '.join(persona_data.get('interests', []) or [])}</p>
                            <p><strong>📱 Platforms I Use:</strong> {', '.join(persona_data.get('platforms', []) or [])}</p>
                        </div>
                        <div class="creative-section">
                            <h2>🚀 What Drives Me</h2>
                            <p><strong>🎯 My Goals:</strong> {persona_data.get('goals', '')}</p>
                            <p><strong>💡 My Motivations:</strong> {persona_data.get('motivations', '')}</p>
                        </div>
                        <div class="creative-section">
                            <h2>🚧 My Challenges</h2>
                            <p><strong>😠 Frustrations:</strong> {persona_data.get('frustrations', '')}</p>
                            <p><strong>💔 Pain Points:</strong> {persona_data.get('pain_points', '')}</p>
                            <p><strong>✅ My Needs:</strong> {persona_data.get('needs', '')}</p>
                            <p><strong> skills:</strong> {persona_data.get('skills', '')}</p>
                        </div>
                    </div>
                </body>
                </html>
                """.strip()

EMPTY_TEMPLATE = """
                <html>
                    <head>
                        <style> body {{ font-family: sans-serif; }} </style>
                    </head>
                    <body>
                        <h1>{persona_data.get('name', 'User Persona')}</h1>
                        <p>Occupation: {persona_data.get('occupation', '')}</p>
                    </body>
                </html>
                """.strip()
