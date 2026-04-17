# -*- coding: utf-8 -*-
"""
Mock LLM — Giả lập câu trả lời của AI để chạy offline không cần API Key.
"""
import time

def ask(question: str) -> str:
    """
    Giả lập quá trình suy nghĩ và trả lời của AI.
    """
    # Giả lập độ trễ của mạng 
    time.sleep(0.5)
    
    responses = {
        "hello": "Xin chào! Tôi là trợ lý AI giả lập của bạn. Tôi đang chạy trên Docker!",
        "health": "Hệ thống đang hoạt động tốt.",
        "redis": "Redis là một kho lưu trữ dữ liệu cấu trúc trong bộ nhớ, dùng để làm database, cache và message broker.",
        "deployment": "Triển khai Agent lên Cloud giúp ứng dụng của bạn có thể truy cập từ bất cứ đâu."
    }
    
    # Tìm câu trả lời phù hợp hoặc trả về câu mặc định
    question_lower = question.lower()
    for key in responses:
        if key in question_lower:
            return responses[key]
            
    return f"Đây là câu trả lời giả lập cho câu hỏi: '{question}'. Trong thực tế, đây sẽ là nơi gọi GPT-4."