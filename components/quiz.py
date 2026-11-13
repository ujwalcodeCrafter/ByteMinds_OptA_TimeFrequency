"""
NeuroLab Knowledge Check - Interactive Educational Quiz.

Interactive 10+ question multiple-choice quiz covering EEG time-frequency
analysis, mathematical trade-offs, and BCI applications.
"""
import streamlit as st


QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "What does a Time-Frequency Representation (TFR) display that an ordinary Fourier Transform (FFT) does not?",
        "options": [
            "The exact scalp coordinates of electrodes",
            "How spectral power at various frequencies evolves over time",
            "The total impedance of EEG electrodes",
            "The blood-oxygen-level-dependent (BOLD) response"
        ],
        "correct_idx": 1,
        "explanation": "Ordinary FFT integrates over the entire time window, producing a static spectrum without timing information. A TFR provides a 2D surface showing how frequency and power change dynamically over time."
    },
    {
        "id": 2,
        "question": "Which EEG frequency band is characterized by 8–13 Hz oscillations, most prominent over occipital electrodes during relaxed wakefulness with eyes closed?",
        "options": [
            "Theta band",
            "Delta band",
            "Alpha band",
            "Beta band"
        ],
        "correct_idx": 2,
        "explanation": "Alpha band (8–13 Hz) is dominant over occipital areas during eyes-closed relaxation and blocks/desynchronizes when eyes open."
    },
    {
        "id": 3,
        "question": "What happens when you INCREASE the number of cycles ('n_cycles') in Morlet wavelet analysis?",
        "options": [
            "Frequency resolution improves, but temporal resolution worsens",
            "Temporal resolution improves, but frequency resolution worsens",
            "Both frequency and temporal resolution improve simultaneously",
            "The sampling frequency of the recording is artificially doubled"
        ],
        "correct_idx": 0,
        "explanation": "More wavelet cycles mean the wavelet spans a longer time window (wider Gaussian envelope). This sharpens frequency resolution (narrower Δf) but blurs temporal localization (larger Δt)."
    },
    {
        "id": 4,
        "question": "In Brain-Computer Interfaces based on Motor Imagery, what does Event-Related Desynchronization (ERD) represent?",
        "options": [
            "A sudden spike in muscle artifact amplitude",
            "A decrease in oscillatory power (e.g. mu/beta) over the contralateral motor cortex due to neuronal activation",
            "Complete electrical silence across the entire brain",
            "An increase in skull impedance during cognitive effort"
        ],
        "correct_idx": 1,
        "explanation": "ERD reflects an event-induced drop in synchronized oscillatory amplitude (power reduction) as cortical networks actively engage in motor planning or execution."
    },
    {
        "id": 5,
        "question": "What fundamental principle prevents achieving simultaneously infinite resolution in both time and frequency?",
        "options": [
            "Ohm's Law",
            "Gabor-Heisenberg Uncertainty Principle",
            "Nyquist-Shannon Sampling Theorem",
            "Weber-Fechner Law"
        ],
        "correct_idx": 1,
        "explanation": "The Gabor-Heisenberg uncertainty principle dictates that the product of time resolution (Δt) and frequency bandwidth (Δf) is bounded: Δt · Δf ≥ 1/(4π)."
    },
    {
        "id": 6,
        "question": "What is the primary advantage of Multitaper Spectral Analysis over standard single-window STFT?",
        "options": [
            "It eliminates the need for electrode gel",
            "It computes spectral estimates with multiple orthogonal tapers, substantially reducing variance and noise",
            "It can record EEG signals without an analog-to-digital converter",
            "It only works on non-human primates"
        ],
        "correct_idx": 1,
        "explanation": "Multitaper uses orthogonal Discrete Prolate Spheroidal Sequences (DPSS) to calculate independent eigenspectra, which are averaged to dramatically lower the estimate's variance."
    },
    {
        "id": 7,
        "question": "Why is baseline correction frequently applied in EEG time-frequency analysis (e.g. converting to decibels or percent change)?",
        "options": [
            "To remove 60 Hz line noise completely",
            "To normalize the 1/f spectral slope and isolate task-induced relative power perturbations",
            "Because raw EEG voltages are too dangerous to plot directly",
            "To convert continuous EEG into discrete audio waves"
        ],
        "correct_idx": 1,
        "explanation": "Due to the 1/f power law, low frequencies carry vastly more raw power than high frequencies. Baseline correction normalizes this disparity so subtle event-related fluctuations (ERD/ERS) become apparent."
    },
    {
        "id": 8,
        "question": "If an EEG signal is sampled at 256 Hz, what is the theoretical maximum frequency (Nyquist limit) that can be analyzed without aliasing?",
        "options": [
            "256 Hz",
            "512 Hz",
            "128 Hz",
            "64 Hz"
        ],
        "correct_idx": 2,
        "explanation": "By the Nyquist-Shannon sampling theorem, the Nyquist frequency is exactly half of the sampling rate: f_Nyquist = 256 / 2 = 128 Hz."
    },
    {
        "id": 9,
        "question": "What is the typical physiological frequency range and characteristic state for Beta waves?",
        "options": [
            "0.5–4 Hz; deep coma or stage N3 sleep",
            "4–8 Hz; hypnagogic meditation and memory encoding",
            "13–30 Hz; active thinking, motor planning, and alertness",
            "80–200 Hz; slow cortical potentials"
        ],
        "correct_idx": 2,
        "explanation": "Beta waves span 13–30 Hz and are associated with active mental concentration, alertness, and motor cortex excitability (sensorimotor rhythms)."
    },
    {
        "id": 10,
        "question": "In a Short-Time Fourier Transform (STFT), what is the direct consequence of shortening the analysis window length (e.g., from 512 to 64 samples)?",
        "options": [
            "Frequency resolution becomes finer, but temporal resolution is lost",
            "Temporal resolution becomes finer, but frequency resolution degrades (coarser bins)",
            "The signal becomes amplified by 20 dB",
            "The phase of the signal is permanently inverted"
        ],
        "correct_idx": 1,
        "explanation": "Short windows confine the Fourier transform to a tight temporal epoch (fine temporal resolution), but fewer cycles fit inside the window, broadening the frequency bin width (degraded frequency resolution)."
    }
]


def render_quiz():
    """Render the interactive quiz module."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">✅ Knowledge Check: Time-Frequency Mastery</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            Test your scientific understanding of EEG time-frequency principles, Morlet wavelets, 
            STFT trade-offs, ERD/ERS dynamics, and BCI paradigms.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for quiz
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
        
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Restart Quiz", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

    total_questions = len(QUIZ_QUESTIONS)
    
    # Render all questions
    for i, q in enumerate(QUIZ_QUESTIONS):
        q_id = q["id"]
        st.markdown(f"#### Question {i+1} of {total_questions}")
        st.markdown(f"**{q['question']}**")
        
        current_selection = st.session_state.quiz_answers.get(q_id, None)
        
        # User answer selection
        selected_option = st.radio(
            f"Select your answer for Question {i+1}:",
            options=q["options"],
            index=q["options"].index(current_selection) if current_selection in q["options"] else None,
            key=f"q_{q_id}",
            disabled=st.session_state.quiz_submitted
        )
        
        if selected_option:
            st.session_state.quiz_answers[q_id] = selected_option
            
        # If quiz submitted, reveal correctness and explanation
        if st.session_state.quiz_submitted:
            correct_answer = q["options"][q["correct_idx"]]
            user_answer = st.session_state.quiz_answers.get(q_id, None)
            
            if user_answer == correct_answer:
                st.success(f"✅ **Correct!** {q['explanation']}")
            else:
                st.error(f"❌ **Incorrect.** Correct answer: **{correct_answer}**\n\n*Why:* {q['explanation']}")
                
        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1rem 0;'>", unsafe_allow_html=True)
        
    # Submit button
    if not st.session_state.quiz_submitted:
        answered_count = len(st.session_state.quiz_answers)
        st.info(f"Answered: {answered_count} / {total_questions} questions")
        if st.button("📝 Submit Answers for Grading", type="primary", use_container_width=True):
            st.session_state.quiz_submitted = True
            st.rerun()
    else:
        # Score calculation
        score = sum(
            1 for q in QUIZ_QUESTIONS 
            if st.session_state.quiz_answers.get(q["id"]) == q["options"][q["correct_idx"]]
        )
        percentage = (score / total_questions) * 100
        
        st.markdown("### 🏆 Final Quiz Result")
        score_color = "#4CAF50" if percentage >= 80 else ("#FF9800" if percentage >= 50 else "#F44336")
        
        st.markdown(f"""
        <div style="background: rgba(10, 25, 47, 0.8); border: 2px solid {score_color}; border-radius: 10px; padding: 1.5rem; text-align: center;">
            <h1 style="color: {score_color}; margin: 0; font-size: 3rem;">{score} / {total_questions}</h1>
            <h3 style="color: #ECEFF1; margin-top: 0.5rem;">Score: {percentage:.0f}%</h3>
            <p style="color: #B0BEC5;">
                {'Outstanding mastery of BCI Time-Frequency Analysis!' if percentage >= 80 else ('Good effort! Review the Explain panel to strengthen concepts.' if percentage >= 50 else 'Keep practicing! Check the Learn the Concepts tab and retry.')}
            </p>
        </div>
        """, unsafe_allow_html=True)
