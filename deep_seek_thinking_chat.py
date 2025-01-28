import gradio as gr
from openai import OpenAI
import re

client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')

def process_response(full_response):
    """Simplified response processing"""
    if "##FINAL_ANSWER##" in full_response:
        thinking, answer = full_response.split("##FINAL_ANSWER##", 1)
        return thinking.strip(), answer.strip()
    return "", full_response.strip()

def chat_with_model(message, chat_history, thinking_placeholder):
    system_prompt = """You are a helpful assistant. First think through the problem, then provide a final answer after ||ANSWER||"""
    
    chat_history.append((message, ""))
    full_response = ""
    thinking_steps = ""
    
    try:
        stream = client.chat.completions.create(
            model="deepseek-r1:7b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            stream=True,
            temperature=0.7
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                full_response += chunk_text
                
                # Update both components as a list
                current_thinking, current_answer = process_response(full_response)
                yield [chat_history + [(None, current_answer)], current_thinking]

        # Final update with cleaned response
        final_thinking, final_answer = process_response(full_response)
        chat_history[-1] = (message, final_answer)
        yield [chat_history, final_thinking]

    except Exception as e:
        print(f"Error: {str(e)}")
        yield [chat_history + [(None, f"Error: {str(e)}")], ""]

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## DeepSeek Chat (Fixed Version)")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Conversation", height=400)
            with gr.Row():
                msg = gr.Textbox(label="Your Message", placeholder="Type here...", show_label=False)
                submit_btn = gr.Button("Submit", variant="primary")
        
        with gr.Column(scale=1):
            thinking = gr.Textbox(
                label="Thinking Process",
                interactive=False,
                lines=15,
                show_copy_button=True
            )

    # Event handlers
    msg.submit(
        fn=chat_with_model,
        inputs=[msg, chatbot, thinking],
        outputs=[chatbot, thinking],
        show_progress="hidden"
    ).then(lambda: gr.Textbox(value=""), outputs=msg)
    
    submit_btn.click(
        fn=chat_with_model,
        inputs=[msg, chatbot, thinking],
        outputs=[chatbot, thinking],
        show_progress="hidden"
    ).then(lambda: gr.Textbox(value=""), outputs=msg)

if __name__ == "__main__":
    demo.launch(share=True)