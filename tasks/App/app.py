import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from tasks.Document_Ingestion.Document_Ingestion import DocumentProcessor
from tasks.Embeddings.Embedding import EmbeddingClient
from tasks.Data_Pipeline.data_pipeline import ChromaCollectionCreator
from tasks.Quiz_Generator.quiz_generator import QuizGenerator
from tasks.Quiz_Manager.quiz_manager import QuizManager

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

import base64

if __name__ == "__main__":
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "PROJECT-123",
        "key_file_path": "C:/path/to/the/json/authentication.json",
        "location": "us-central1"
    }
    
    # Add Session State
    if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
        
        st.session_state["question_bank"] = []
    
        screen = st.empty()
        with screen.container():
            st.markdown("<h1 style='text-align: center;'>Quizzo</h1>", unsafe_allow_html=True)
            st.header("Quiz Builder")
            
            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                
                processor = DocumentProcessor()
                processor.ingest_documents()
            
                embed_client = EmbeddingClient(**embed_config) 
            
                chroma_creator = ChromaCollectionCreator(processor, embed_client)
              
                topic_input= st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                num_questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
                    
                submitted = st.form_submit_button("Generate")
                
                if submitted:
                    with st.spinner("Processing..."):
                        chroma_creator.create_chroma_collection()
                            
                        if len(processor.pages) > 0:
                            st.success(f"Generating {num_questions} question(s) for topic: {topic_input}", icon=":material/pending:")
                        
                        generator = QuizGenerator(topic_input, num_questions, chroma_creator)
                        question_bank = generator.generate_quiz()
                    
                        st.session_state["question_bank"] = question_bank

                        
                        st.session_state["display_quiz"] = True

                   
                        st.session_state["question_index"] = 0
                        st.rerun()
    
    
    elif "display_quiz" in st.session_state and st.session_state["display_quiz"]:
        st.empty()
        with st.container():
            st.markdown("<h1 style='text-align: center;'>Quizzo</h1>", unsafe_allow_html=True)
            st.header(f"Quiz Question {st.session_state['question_index']+1}: ")
            quiz_manager = QuizManager(st.session_state["question_bank"])
            
            # Format the question and display it
            with st.form("MCQ"):
             
                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])
             
                
                # Unpack choices for radio button
                choices = []
                for choice in index_question['choices']:
                    key = choice['key']
                    value = choice['value']
                    choices.append(f"{key}) {value}")
                
                # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio(
                    "Choose an answer",
                    choices,
                    index = None
                )
                
                st.session_state["correct_answers"] = 0
                st.session_state["incorrect_answers"] = 0
                st.write("")

                column1,column2,column3 = st.columns([4,6,3])
                c1,c2,c3 = column2.columns([2,3,2])
                answer_choice = c2.form_submit_button("Check")

                
                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                        st.session_state["correct_answers"] += 1
                    else:
                        st.error("Incorrect!")
                        st.session_state["incorrect_answers"] += 1
                    st.write(f"Explanation: {index_question['explanation']}")


                if st.session_state['question_index'] > 0:
                    column1.form_submit_button("Previous Question", on_click=lambda: quiz_manager.next_question_index(direction=-1))
                
                if answer is not None and st.session_state['question_index'] < len(quiz_manager.questions) - 1:
                    column3.form_submit_button("Next Question", on_click=lambda: quiz_manager.next_question_index(direction=1))
                    
                if st.session_state['question_index'] == len(quiz_manager.questions)-1:
                    if column3.form_submit_button("Generate Report", on_click=lambda: quiz_manager.next_question_index(direction=0)):
                        c = canvas.Canvas("report.pdf", pagesize=letter)

                        c.setFont("Helvetica", 24)
                        c.drawCentredString(4.25 * inch, 10.5 * inch, "Quizzo")
                        c.setFont("Helvetica", 24)
                        c.drawString(30, 720, "Quiz Report")

                        c.setFont("Helvetica", 14)
                        c.drawString(30, 680, f"Total questions: {len(quiz_manager.questions)}")

                        # Add the number of correct answers
                        c.drawString(30, 655, f"Correct answers: {st.session_state['correct_answers']}")

                        # Add the number of incorrect answers
                        c.drawString(30, 625, f"Incorrect answers: {st.session_state['incorrect_answers']}")

                        score = st.session_state['correct_answers'] / len(quiz_manager.questions) * 100
                        c.drawString(30, 600, f"Score: {score:.2f}%")

                        c.save()
                        with open("report.pdf", "rb") as f:
                            pdf_bytes = f.read()

                        # Create a download button for the PDF file
                        b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="report.pdf">Download Quiz Report</a>'
                        st.markdown(href, unsafe_allow_html=True)

                progress = (st.session_state['question_index'] / len(quiz_manager.questions))

                # Display the progress bar
                st.progress(progress)
                st.markdown(f'<div style="width: 100%; height: 20px; position: relative;">'
                f'<div style="position: absolute; left: {progress * 100}%; top: -20px;">{progress * 100:.0f}%</div>'
                f'</div>',unsafe_allow_html=True)
