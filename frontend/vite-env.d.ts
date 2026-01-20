/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly OPENAI_API_KEY: string;
  readonly ANTHROPIC_API_KEY: string;
  readonly LLM_PROVIDER: 'openai' | 'anthropic' | 'vllm';
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}