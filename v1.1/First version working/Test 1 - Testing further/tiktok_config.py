# tiktok_config.py
# Part 1: Emotions and Story Frameworks
import random  # Added import

from dataclasses import dataclass
from typing import List, Dict, Optional, Union

@dataclass
class TikTokStyle:
    name: str
    description: str
    typical_duration: tuple[int, int]  # (min_seconds, max_seconds)
    suitable_emotions: List[str]

# Enhanced emotion system with detailed categorization
EMOTIONS = {
    "High Energy": [
        "Excited",
        "Enthusiastic",
        "Passionate",
        "Energetic",
        "Hyped",
        "Amazed",
        "Thrilled",
        "Ecstatic",
        "Fired-up",
        "Animated",
        "Dynamic",
        "Vibrant"
    ],
    "Dramatic": [
        "Shocked",
        "Surprised",
        "Dramatic",
        "Suspenseful",
        "Mind-blown",
        "Astonished",
        "Stunned",
        "Flabbergasted",
        "Speechless",
        "Bewildered",
        "Intense",
        "Theatrical"
    ],
    "Informative": [
        "Knowledgeable",
        "Expert",
        "Professional",
        "Educational",
        "Analytical",
        "Insightful",
        "Authoritative",
        "Instructional",
        "Methodical",
        "Technical",
        "Scientific",
        "Academic"
    ],
    "Relatable": [
        "Casual",
        "Friendly",
        "Humorous",
        "Sarcastic",
        "Empathetic",
        "Down-to-earth",
        "Authentic",
        "Genuine",
        "Approachable",
        "Understanding",
        "Sympathetic",
        "Real"
    ],
    "Storytelling": [
        "Mysterious",
        "Intriguing",
        "Narrative",
        "Descriptive",
        "Engaging",
        "Captivating",
        "Suspenseful",
        "Dramatic",
        "Compelling",
        "Enchanting",
        "Immersive",
        "Gripping"
    ],
    "Inspirational": [
        "Motivating",
        "Uplifting",
        "Encouraging",
        "Empowering",
        "Inspiring",
        "Hopeful",
        "Positive",
        "Optimistic",
        "Transformative",
        "Life-changing",
        "Influential",
        "Moving"
    ],
    "Humorous": [
        "Funny",
        "Comedic",
        "Witty",
        "Playful",
        "Light-hearted",
        "Silly",
        "Goofy",
        "Entertaining",
        "Amusing",
        "Whimsical",
        "Satirical",
        "Ironic"
    ],
    "Contemplative": [
        "Thoughtful",
        "Reflective",
        "Philosophical",
        "Deep",
        "Introspective",
        "Mindful",
        "Perspective",
        "Analytical",
        "Questioning",
        "Pondering",
        "Meditative",
        "Intellectual"
    ],
    "Controversial": [
        "Provocative",
        "Challenging",
        "Debatable",
        "Thought-provoking",
        "Critical",
        "Questioning",
        "Skeptical",
        "Analytical",
        "Investigative",
        "Exposing",
        "Revolutionary",
        "Ground-breaking"
    ],
    "Trendy": [
        "Current",
        "Popular",
        "Viral",
        "Hip",
        "Modern",
        "Fresh",
        "Cool",
        "Contemporary",
        "Cutting-edge",
        "In-vogue",
        "Fashionable",
        "Trending"
    ]
}

# Expanded Story Frameworks
STORY_FRAMEWORKS = {
    "Problem-Solution": {
        "structure": [
            "Hook: {pain_point_hook}",
            "Problem Identification: {relatable_problem}",
            "Impact Description: {why_it_matters}",
            "Solution Teaser: Here's what changed everything...",
            "Solution Steps: {detailed_steps}",
            "Results Preview: {benefits}",
            "Proof/Demonstration: {evidence}",
            "Conclusion: {transformation}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (30, 60),
        "best_emotions": ["Informative", "Relatable", "Inspirational"]
    },
    "Before-After": {
        "structure": [
            "Hook: {transformation_hook}",
            "Before State: {pain_points}",
            "Turning Point: {catalyst}",
            "Process Overview: {what_changed}",
            "Key Steps: {major_changes}",
            "After State: {results}",
            "Validation: {proof}",
            "Inspiration: {motivation}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (20, 45),
        "best_emotions": ["Dramatic", "Inspirational", "High Energy"]
    },
    "Day-In-Life": {
        "structure": [
            "Hook: {lifestyle_hook}",
            "Morning Routine: {morning}",
            "Main Activities: {daily_highlights}",
            "Challenges: {obstacles}",
            "Solutions: {how_handled}",
            "Tips & Tricks: {life_hacks}",
            "Results: {achievements}",
            "Reflection: {lessons}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (45, 120),
        "best_emotions": ["Relatable", "Trendy", "Inspirational"]
    },
    "Tutorial": {
        "structure": [
            "Hook: {value_hook}",
            "Overview: {what_learning}",
            "Materials/Requirements: {needed_items}",
            "Step-by-Step: {detailed_steps}",
            "Tips: {pro_tips}",
            "Common Mistakes: {warnings}",
            "Final Result: {outcome}",
            "Variations: {alternatives}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (45, 120),
        "best_emotions": ["Informative", "Educational", "Friendly"]
    },
    "Behind-the-Scenes": {
        "structure": [
            "Hook: {curiosity_hook}",
            "Context: {background}",
            "Setup Reveal: {preparation}",
            "Process Insights: {inside_look}",
            "Challenges: {difficulties}",
            "Solutions: {overcame}",
            "Final Product: {result}",
            "Tips & Secrets: {insider_tips}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (30, 90),
        "best_emotions": ["Authentic", "Engaging", "Mysterious"]
    },
    "Myth-Busting": {
        "structure": [
            "Hook: {myth_hook}",
            "Common Belief: {misconception}",
            "Why It's Wrong: {truth}",
            "Evidence: {proof}",
            "Real Explanation: {facts}",
            "Examples: {demonstrations}",
            "Tips: {correct_approach}",
            "Summary: {key_takeaways}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (30, 60),
        "best_emotions": ["Dramatic", "Informative", "Surprising"]
    },
    "Story Time": {
        "structure": [
            "Hook: {dramatic_hook}",
            "Setup: {context}",
            "Build-up: {rising_action}",
            "Conflict: {challenge}",
            "Climax: {peak_moment}",
            "Resolution: {outcome}",
            "Lesson: {moral}",
            "Reflection: {thoughts}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (45, 90),
        "best_emotions": ["Storytelling", "Dramatic", "Engaging"]
    },
    "Product Review": {
        "structure": [
            "Hook: {review_hook}",
            "Product Intro: {what_testing}",
            "First Impressions: {initial_thoughts}",
            "Testing Process: {how_tested}",
            "Pros: {benefits}",
            "Cons: {drawbacks}",
            "Comparisons: {alternatives}",
            "Verdict: {final_thoughts}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (30, 60),
        "best_emotions": ["Honest", "Analytical", "Informative"]
    },
    "Reaction": {
        "structure": [
            "Hook: {reaction_hook}",
            "Context: {what_reacting_to}",
            "Initial Response: {first_impression}",
            "Deep Dive: {detailed_thoughts}",
            "Highlights: {best_moments}",
            "Critiques: {concerns}",
            "Analysis: {breakdown}",
            "Final Thoughts: {conclusion}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (20, 45),
        "best_emotions": ["Dramatic", "Authentic", "Engaging"]
    },
    "Challenge": {
        "structure": [
            "Hook: {challenge_hook}",
            "Challenge Intro: {what_attempting}",
            "Preparation: {setup}",
            "Attempt: {execution}",
            "Struggles: {difficulties}",
            "Breakthroughs: {successes}",
            "Results: {outcome}",
            "Tips: {advice}",
            "Call to Action: {outro}"
        ],
        "typical_duration": (30, 60),
        "best_emotions": ["High Energy", "Entertaining", "Dramatic"]
    }
}

# Video Structures with detailed timing and components
VIDEO_STRUCTURES = {
    "Hook-Content-CTA": {
        "structure": [
            "Pattern Interrupt (2-3s): {attention_grab}",
            "Hook Statement (3-5s): {hook}",
            "Value Promise (3-5s): {what_they_get}",
            "Main Content (15-35s): {content}",
            "Key Takeaway (5-7s): {summary}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (30, 50),
        "best_for": ["Tips", "Hacks", "Quick Tutorials"]
    },
    "Question-Answer": {
        "structure": [
            "Question Hook (3-5s): {question}",
            "Intrigue Builder (3-5s): 'The answer might surprise you...'",
            "Context Setup (5-8s): {background}",
            "Answer Reveal (10-15s): {answer}",
            "Explanation (10-20s): {explanation}",
            "Proof/Examples (8-12s): {evidence}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (40, 70),
        "best_for": ["Educational", "Myth Busting", "Facts"]
    },
    "Trend Adaptation": {
        "structure": [
            "Trend Reference (3-5s): {trend_intro}",
            "Your Twist (5-7s): {unique_angle}",
            "Setup (5-8s): {preparation}",
            "Execution (15-25s): {content}",
            "Reaction (5-8s): {response}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (35, 60),
        "best_for": ["Challenges", "Dance", "Music"]
    },
    "Educational-Steps": {
        "structure": [
            "Knowledge Hook (3-5s): {hook}",
            "Problem Statement (5-7s): {issue}",
            "Step 1 (8-10s): {first_step}",
            "Step 2 (8-10s): {second_step}",
            "Step 3 (8-10s): {third_step}",
            "Result Demo (5-8s): {outcome}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (40, 55),
        "best_for": ["Tutorials", "DIY", "How-To"]
    },
    "Storytime": {
        "structure": [
            "Hook Phrase (3-5s): {hook}",
            "Setting Scene (5-8s): {context}",
            "Build Up (10-15s): {development}",
            "Plot Twist (5-8s): {twist}",
            "Resolution (10-15s): {ending}",
            "Lesson/Moral (5-7s): {takeaway}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (45, 60),
        "best_for": ["Personal Stories", "Experiences", "Lessons"]
    },
    "Review-Style": {
        "structure": [
            "Product Intro (3-5s): {item}",
            "First Impression (5-7s): {initial_thoughts}",
            "Key Features (10-15s): {features}",
            "Testing (10-15s): {testing}",
            "Pros/Cons (8-10s): {evaluation}",
            "Verdict (5-7s): {conclusion}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (45, 65),
        "best_for": ["Product Reviews", "Comparisons", "Recommendations"]
    },
    "Transformation": {
        "structure": [
            "Before Shot (3-5s): {before}",
            "Pain Points (5-7s): {problems}",
            "Process Highlights (15-20s): {process}",
            "Challenges (5-8s): {difficulties}",
            "After Reveal (5-8s): {after}",
            "Tips (5-7s): {advice}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (40, 60),
        "best_for": ["Makeovers", "Before/After", "Progress"]
    },
    "Comedy-Sketch": {
        "structure": [
            "Setup (3-5s): {situation}",
            "Character Intro (3-5s): {character}",
            "Build-Up (10-15s): {development}",
            "Punchline (5-7s): {joke}",
            "Reaction (5-7s): {response}",
            "Tag (3-5s): {additional_joke}",
            "Call to Action (3-5s): {outro}"
        ],
        "typical_duration": (30, 50),
        "best_for": ["Comedy", "Skits", "Parody"]
    }
}

# Expanded Hook Types with more variants and use cases
HOOK_TYPES = {
    "Question": {
        "description": "Opens with an engaging question to create curiosity",
        "templates": [
            "Want to know how {topic}?",
            "Did you know this about {topic}?",
            "Ever wondered why {topic}?",
            "What if I told you about {topic}?",
            "Ready to discover the truth about {topic}?",
            "Curious about {topic}?",
            "Have you been doing {topic} wrong?",
            "Can you guess what happens when {topic}?",
            "Why do most people fail at {topic}?",
            "Is this the best way to {topic}?",
            "What's the real secret to {topic}?",
            "How did I master {topic}?",
            "Want to level up your {topic}?",
            "Are you making these {topic} mistakes?",
            "Did you know this {topic} hack exists?"
        ],
        "best_for": ["Educational", "Tutorial", "Myth-Busting", "Tips"],
        "emotional_tone": ["Curious", "Intriguing", "Thought-provoking"]
    },
    "Statement": {
        "description": "Strong, authoritative opening statement",
        "templates": [
            "This {topic} hack changed everything...",
            "Nobody talks about this {topic} secret...",
            "Here's what they don't tell you about {topic}...",
            "The truth about {topic} that shocked me...",
            "I discovered something crazy about {topic}...",
            "This {topic} technique is a game-changer...",
            "Let me show you the real way to {topic}...",
            "I've been doing {topic} wrong for years...",
            "This is how pros do {topic}...",
            "The industry secrets about {topic}...",
            "I found a better way to {topic}...",
            "The hidden truth about {topic}...",
            "What experts won't tell you about {topic}...",
            "The fastest way to master {topic}...",
            "This changes everything about {topic}..."
        ],
        "best_for": ["Story Time", "Behind-the-Scenes", "Tutorials"],
        "emotional_tone": ["Confident", "Authoritative", "Revealing"]
    },
    "Shocking": {
        "description": "Surprising or unexpected opening to grab attention",
        "templates": [
            "I can't believe this {topic} fact...",
            "This {topic} revelation shocked me...",
            "Everything you know about {topic} is wrong...",
            "The {topic} industry doesn't want you to know...",
            "You won't believe what I found about {topic}...",
            "This {topic} secret will blow your mind...",
            "The shocking truth about {topic}...",
            "Warning: This {topic} fact will surprise you...",
            "I was shocked when I learned this about {topic}...",
            "This {topic} discovery changed everything...",
            "The scary truth about {topic}...",
            "They've been lying about {topic}...",
            "What they're hiding about {topic}...",
            "The dark side of {topic}...",
            "This {topic} secret is mindblowing..."
        ],
        "best_for": ["Reaction", "Myth-Busting", "Revelations"],
        "emotional_tone": ["Dramatic", "Surprising", "Intense"]
    },
    "Action": {
        "description": "Immediate call to action or command",
        "templates": [
            "Stop scrolling! This {topic} tip is important...",
            "You need to try this {topic} hack right now...",
            "Watch this before you {topic} again...",
            "Don't make another {topic} mistake...",
            "Drop everything and watch this {topic} hack...",
            "This {topic} trick will change your life...",
            "Run, don't walk, to try this {topic} technique...",
            "You're missing out on this {topic} secret...",
            "Listen up! This {topic} hack is golden...",
            "Grab your phone and try this {topic} trick...",
            "Don't scroll past this {topic} tip...",
            "Save this {topic} hack now...",
            "You'll regret missing this {topic} secret...",
            "Quick! Try this {topic} technique before others...",
            "Start doing this {topic} hack today..."
        ],
        "best_for": ["Tutorial", "Tips", "Life Hacks"],
        "emotional_tone": ["Urgent", "Commanding", "Energetic"]
    },
    "Statistics": {
        "description": "Opens with a compelling number or statistic",
        "templates": [
            "Only {number}% of people know this {topic} trick...",
            "{number} out of {total} fail at {topic}...",
            "I made ${amount} using this {topic} method...",
            "This {topic} hack saves me {number} hours...",
            "{number} people tried this {topic} test...",
            "I tested {number} {topic} methods...",
            "After {number} years of {topic}...",
            "{percentage}% improvement in {topic}...",
            "Tried {number} {topic} hacks, this one worked...",
            "Save {amount} on {topic} with this trick...",
            "{number} experts agree on this {topic} fact...",
            "This {topic} hack is used by top {percentage}%...",
            "Increased my {topic} by {number}x...",
            "Lost {number} hours to {topic} until...",
            "Tested for {number} days: here's what happened..."
        ],
        "best_for": ["Data-Driven", "Results", "Case Studies"],
        "emotional_tone": ["Factual", "Impressive", "Credible"]
    },
    "Story": {
        "description": "Opens with a personal narrative hook",
        "templates": [
            "Last week, I discovered something about {topic}...",
            "My {topic} journey started when...",
            "Here's how {topic} changed my life...",
            "The day I learned the truth about {topic}...",
            "My biggest {topic} mistake taught me...",
            "After failing at {topic} 100 times...",
            "What my mom never told me about {topic}...",
            "The {topic} secret I learned the hard way...",
            "My embarrassing {topic} story...",
            "How I went from {topic} newbie to pro...",
            "The moment that changed my {topic} forever...",
            "My {topic} transformation started here...",
            "The {topic} trick I wish I knew sooner...",
            "My first attempt at {topic} was a disaster...",
            "The day I mastered {topic}..."
        ],
        "best_for": ["Personal Stories", "Transformations", "Lessons"],
        "emotional_tone": ["Personal", "Authentic", "Relatable"]
    },
    "Controversial": {
        "description": "Opens with a debatable or provocative statement",
        "templates": [
            "Unpopular opinion about {topic}...",
            "Why everyone is wrong about {topic}...",
            "The {topic} debate ends here...",
            "Stop believing these {topic} lies...",
            "The controversial truth about {topic}...",
            "Why I disagree with {topic} experts...",
            "The {topic} myth you need to stop believing...",
            "Here's why {topic} advice is wrong...",
            "The real reason {topic} isn't working...",
            "What no one admits about {topic}...",
            "The {topic} conspiracy exposed...",
            "Why {topic} gurus are misleading you...",
            "The uncomfortable truth about {topic}...",
            "Time to debunk this {topic} myth...",
            "Why I'm calling out {topic} fake experts..."
        ],
        "best_for": ["Debates", "Myth-Busting", "Hot Takes"],
        "emotional_tone": ["Provocative", "Critical", "Bold"]
    },
    "FOMO": {
        "description": "Creates fear of missing out",
        "templates": [
            "If you're not doing this {topic} hack...",
            "Don't miss out on this {topic} secret...",
            "The {topic} trend that's about to explode...",
            "Why everyone is trying this {topic} method...",
            "The {topic} hack going viral right now...",
            "This {topic} secret won't last long...",
            "The {topic} opportunity you're missing...",
            "Why you need to start {topic} today...",
            "Don't wait to try this {topic} trick...",
            "The {topic} wave you need to catch...",
            "This {topic} hack is blowing up...",
            "Get on this {topic} trend before it's gone...",
            "The {topic} secret everyone's talking about...",
            "You're losing money not knowing this {topic} hack...",
            "Missing out on {topic} benefits? Here's why..."
        ],
        "best_for": ["Trends", "Opportunities", "Time-Sensitive"],
        "emotional_tone": ["Urgent", "Exciting", "Compelling"]
    },
    "Problem-Agitate": {
        "description": "Highlights a problem then offers solution",
        "templates": [
            "Tired of struggling with {topic}?",
            "Frustrated with your {topic} results?",
            "Can't seem to master {topic}?",
            "Is {topic} giving you headaches?",
            "Fed up with {topic} failures?",
            "Done with {topic} disappointments?",
            "Still can't figure out {topic}?",
            "Is {topic} holding you back?",
            "Struggling to understand {topic}?",
            "Wasting time on {topic}?",
            "Not seeing {topic} progress?",
            "Is {topic} stressing you out?",
            "Overwhelmed by {topic}?",
            "Need help with {topic}?",
            "Ready to fix your {topic} problems?"
        ],
        "best_for": ["Solutions", "Problem-Solving", "Help Videos"],
        "emotional_tone": ["Empathetic", "Understanding", "Helpful"]
    }
}

# Part 3A: Enhanced Outro System

OUTROS = {
    "Template": {
        "Call to Action": [
            # Basic CTAs
            "Follow for more {topic} content!",
            "Hit + for part 2!",
            "Drop a 💡 if you learned something new!",
            "Save this for later!",
            "Don't forget to follow for daily {topic} tips!",
            "Share this with someone who needs it!",
            "Double tap if you found this helpful!",
            "Turn on notifications to never miss a {topic} tip!",
            
            # Social Proof CTAs
            "Join {number}k others learning about {topic}!",
            "This helped over {number}k people with {topic}!",
            "The {topic} community loves this trick!",
            "Don't just take my word - read the comments!",
            "We're {number}k strong in the {topic} journey!",
            
            # FOMO-Based
            "Don't miss tomorrow's {topic} secret!",
            "More {topic} hacks coming this week!",
            "Limited time {topic} tips in my next video!",
            "Exclusive {topic} content dropping soon!",
            "Secret {topic} method revealed tomorrow!",
            
            # Value-Based
            "More life-changing {topic} hacks on my profile!",
            "Click my bio for free {topic} resources!",
            "Full {topic} guide in my latest post!",
            "Get my complete {topic} checklist - link in bio!",
            "Unlock more {topic} secrets on my page!"
        ],
        "Engagement": {
            "Questions": [
                "Comment your thoughts below!",
                "What's your experience with {topic}?",
                "Drop your {topic} questions below!",
                "What should I cover next about {topic}?",
                "Scale of 1-10, how helpful was this {topic} tip?",
                "Tag someone who needs these {topic} tips!",
                "What's your biggest {topic} challenge?",
                "Share your best {topic} hack in the comments!",
                "Which {topic} tip surprised you most?",
                "Need help with specific {topic} problems? Ask below!"
            ],
            "Challenges": [
                "Try this {topic} hack and show me your results!",
                "Duet this video with your {topic} attempt!",
                "Show me your {topic} transformation!",
                "Take the {topic} challenge - tag me in your try!",
                "Use this sound for your {topic} video!",
                "Stitch with your {topic} story!",
                "React to this {topic} hack!",
                "Start your {topic} journey today - show me day 1!",
                "Join the {topic} revolution - post your version!",
                "Make this {topic} hack go viral!"
            ],
            "Community Building": [
                "Welcome to the {topic} family!",
                "Join our {topic} community!",
                "Let's master {topic} together!",
                "Support each other's {topic} journey below!",
                "Share your {topic} wins in the comments!",
                "Drop a ❤️ if you're part of the {topic} gang!",
                "Tag your {topic} accountability partner!",
                "Build your {topic} network - connect below!",
                "Share this with your {topic} study group!",
                "Let's grow our {topic} skills together!"
            ]
        },
        "Series Continuation": {
            "Part Announcements": [
                "Part {number} drops tomorrow!",
                "More {topic} secrets in part {number}!",
                "Like for part {number}!",
                "Next part at {number}k likes!",
                "Comment '📝' for part {number}!"
            ],
            "Series Hooks": [
                "This {topic} series will change your life...",
                "The {topic} journey continues...",
                "Your {topic} transformation starts here...",
                "Level up your {topic} game with this series...",
                "Master {topic} with this tutorial series..."
            ]
        }
    },
    "LLM": {
        "instructions": """
        Generate a creative outro that:
        1. Matches the video's emotion and style
        2. Encourages engagement through:
           - Asking relevant questions
           - Encouraging saves and shares
           - Creating community interaction
           - Promoting discussion
        3. Hints at future content by:
           - Teasing upcoming videos
           - Suggesting related topics
           - Creating anticipation
        4. Feels natural and authentic by:
           - Using conversational language
           - Avoiding forced engagement
           - Being genuine and relatable
        5. Includes appropriate emojis (2-3 max)
        6. Keeps length between 10-15 words
        7. Incorporates one clear call to action
        8. Uses platform-specific language
        
        Style Guidelines:
        - Keep it casual and friendly
        - Use active voice
        - Create urgency without desperation
        - Make it shareable and memorable
        - Focus on value to viewer
        """,
        "engagement_patterns": {
            "Question Types": [
                "Opinion Questions",
                "Experience Questions",
                "Preference Questions",
                "Problem Questions",
                "Future Questions"
            ],
            "Emotion Triggers": [
                "Curiosity",
                "FOMO",
                "Excitement",
                "Connection",
                "Achievement"
            ],
            "Call Types": [
                "Direct Ask",
                "Soft Suggestion",
                "Value Offer",
                "Community Join",
                "Challenge Accept"
            ]
        }
    }
}

# Part 3B: Enhanced Content Categories

CONTENT_CATEGORIES = {
    "Educational": {
        "Academic": [
            "Study Tips",
            "Exam Preparation",
            "Memory Techniques",
            "Note-Taking Methods",
            "Time Management",
            "Subject Tutorials",
            "Learning Hacks",
            "Research Methods"
        ],
        "Professional Skills": [
            "Career Development",
            "Interview Tips",
            "Resume Writing",
            "Public Speaking",
            "Leadership Skills",
            "Networking Tips",
            "Business Etiquette",
            "Workplace Communication"
        ],
        "Life Skills": [
            "Financial Literacy",
            "Time Management",
            "Organization Tips",
            "Problem Solving",
            "Decision Making",
            "Critical Thinking",
            "Emotional Intelligence",
            "Personal Development"
        ],
        "Technical": [
            "Programming Tutorials",
            "Digital Tools",
            "Software Tips",
            "Tech Shortcuts",
            "App Reviews",
            "Hardware Guides",
            "Coding Basics",
            "Tech Troubleshooting"
        ]
    },
    "Entertainment": {
        "Performance": [
            "Dance Choreography",
            "Singing Covers",
            "Comedy Skits",
            "Acting Scenes",
            "Musical Performances",
            "Lip Sync",
            "Talent Showcases",
            "Character Impressions"
        ],
        "Gaming": [
            "Game Reviews",
            "Gaming Tips",
            "Speedruns",
            "Game Reactions",
            "Easter Eggs",
            "Gaming News",
            "Strategy Guides",
            "Gaming Highlights"
        ],
        "Reactions": [
            "Trend Reactions",
            "Video Reactions",
            "News Reactions",
            "Product Testing",
            "Food Tasting",
            "Experience Reviews",
            "Live Reactions",
            "First Impressions"
        ],
        "Challenges": [
            "Dance Challenges",
            "Skill Challenges",
            "Food Challenges",
            "Fitness Challenges",
            "Creative Challenges",
            "Duets",
            "Trending Challenges",
            "Original Challenges"
        ]
    },
    "Lifestyle": {
        "Fashion": [
            "Style Tips",
            "Outfit Ideas",
            "Fashion Hauls",
            "Trend Updates",
            "Wardrobe Hacks",
            "Fashion DIY",
            "Shopping Guide",
            "Season Looks"
        ],
        "Beauty": [
            "Makeup Tutorials",
            "Skincare Routines",
            "Hair Styling",
            "Beauty Hacks",
            "Product Reviews",
            "Natural Beauty",
            "Beauty Tips",
            "Transformation"
        ],
        "Fitness": [
            "Workout Routines",
            "Exercise Tips",
            "Diet Plans",
            "Transformation",
            "Fitness Challenges",
            "Home Workouts",
            "Gym Guide",
            "Sports Training"
        ],
        "Food & Cooking": [
            "Recipe Tutorials",
            "Cooking Hacks",
            "Food Reviews",
            "Kitchen Tips",
            "Meal Prep",
            "Healthy Eating",
            "Baking Guide",
            "Restaurant Reviews"
        ]
    },
    "Creative": {
        "Art & Design": [
            "Art Tutorials",
            "Digital Design",
            "Drawing Tips",
            "Painting Guide",
            "Graphic Design",
            "Animation",
            "Creative Process",
            "Art Challenges"
        ],
        "DIY & Crafts": [
            "Craft Tutorials",
            "DIY Projects",
            "Upcycling",
            "Home Decor",
            "Handmade Items",
            "Gift Ideas",
            "Easy Crafts",
            "Seasonal Projects"
        ],
        "Photography": [
            "Photo Tips",
            "Camera Tricks",
            "Editing Tutorial",
            "Composition Guide",
            "Lighting Setup",
            "Phone Photography",
            "Props Ideas",
            "Photo Challenges"
        ],
        "Music": [
            "Music Production",
            "Instrument Tips",
            "Song Covers",
            "Music Theory",
            "Beat Making",
            "Vocal Training",
            "Music Reviews",
            "Artist Features"
        ]
    },
    "Business & Money": {
        "Entrepreneurship": [
            "Business Tips",
            "Startup Guide",
            "Marketing Strategy",
            "Sales Techniques",
            "Business Models",
            "Success Stories",
            "Growth Hacks",
            "Business Tools"
        ],
        "Finance": [
            "Money Tips",
            "Investment Guide",
            "Saving Strategies",
            "Budgeting Help",
            "Credit Advice",
            "Tax Tips",
            "Wealth Building",
            "Financial Literacy"
        ],
        "Side Hustles": [
            "Online Business",
            "Passive Income",
            "Freelancing Tips",
            "E-commerce Guide",
            "Digital Products",
            "Service Business",
            "Income Streams",
            "Business Ideas"
        ],
        "Career Growth": [
            "Job Search",
            "Interview Prep",
            "Resume Tips",
            "Career Change",
            "Skill Development",
            "Salary Negotiation",
            "Work Life Balance",
            "Professional Growth"
        ]
    }
}

# Add helper functions for content selection
def get_random_topic(category: str, subcategory: str = None) -> str:
    """Get a random topic from specified category/subcategory"""
    if subcategory:
        return random.choice(CONTENT_CATEGORIES[category][subcategory])
    topics = []
    for subcat in CONTENT_CATEGORIES[category].values():
        topics.extend(subcat)
    return random.choice(topics)

def get_trending_combinations() -> List[Dict]:
    """Generate trending content combinations"""
    return [
        {
            "category": cat,
            "subcategory": subcat,
            "topic": topic,
            "hook_type": random.choice(list(HOOK_TYPES.keys())),
            "emotion": random.choice([e for ems in EMOTIONS.values() for e in ems])
        }
        for cat, subcats in CONTENT_CATEGORIES.items()
        for subcat, topics in subcats.items()
        for topic in topics
    ]