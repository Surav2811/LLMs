import gradio as gr
from openai import OpenAI
import time

# Connect to Ollama's OpenAI-compatible API
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama',  # Required but ignored by Ollama
)

def chat_with_model(message, chat_history):
    # Add user message to history
    chat_history.append((message, ""))
    
    # Create the stream with thinking simulation
    full_response = ""
    stream = client.chat.completions.create(
        model="deepseek-r1:7b",
        messages=[{"role": "user", "content": message}],
        stream=True,
    )
    
    # Stream the response
    for chunk in stream:
        if chunk.choices[0].delta.content:
            chunk_text = chunk.choices[0].delta.content
            full_response += chunk_text
            
            # Update the chat history with streaming response
            chat_history[-1] = (message, full_response)
            
            # Create a thinking effect by pausing between chunks
            time.sleep(0.02)
            yield chat_history

# Gradio interface
with gr.Blocks(title="DeepSeek Chat", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# DeepSeek R1:7b Chat Interface")
    
    chatbot = gr.Chatbot(
        height=500,
        bubble_full_width=False,
        show_copy_button=True
    )
    
    msg = gr.Textbox(
        label="Your Message",
        placeholder="Type your message here...",
        autofocus=True
    )
    
    clear = gr.ClearButton([msg, chatbot])

    msg.submit(
        fn=chat_with_model,
        inputs=[msg, chatbot],
        outputs=chatbot,
    ).then(
        lambda: gr.Textbox(value=""),
        outputs=msg
    )

if __name__ == "__main__":
    demo.queue().launch(share=True)