import transformers

chat_tokenizer_dir = r"deepseek_api\deepseek_v2_tokenizer\deepseek_v2_tokenizer"


class offline_tokenizer:
    def __init__(self) -> None:
        self.tokenizer = transformers.AutoTokenizer.from_pretrained( 
            chat_tokenizer_dir, trust_remote_code=True
        )

    def count_tokens(self, text: str) -> int:
        result = self.tokenizer.encode(text)
        return len(result)