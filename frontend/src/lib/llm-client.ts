import OpenAI from 'openai';

const provider = import.meta.env.LLM_PROVIDER || 'vllm';

// vLLM server is OpenAI-compatible, so we use the OpenAI SDK
const client = new OpenAI({
  apiKey: 'not-needed', // vLLM doesn't require auth by default
  baseURL: import.meta.env.VLLM_BASE_URL || 'http://localhost:8000/v1',
  timeout: 30000,
  maxRetries: 1,
});

const MODEL = import.meta.env.VLLM_MODEL || 'Qwen/Qwen3-0.6B';

export async function completeLyric(partialLyric: string): Promise<string> {
  const prompt = `<｜no_think｜>Continue this lyric naturally. Only give the next few words.

"${partialLyric}"

Continue:`;

  const response = await client.chat.completions.create({
    model: MODEL,
    messages: [{ role: 'user', content: prompt }],
    max_tokens: 30,
    temperature: 0.7,
  });

  let completion = response.choices[0]?.message?.content?.trim() || '';
  
  // Remove <think> tags
  completion = completion.replace(/<\/?think>/gi, '').trim();

  // Helper function to normalize text for comparison (remove punctuation)
  const normalize = (text: string) => text.toLowerCase().replace(/[^\w\s]/g, ''); 

  // Remove leading duplicate of the input
  // Check if completion starts with (partial) input text
  const inputWords = partialLyric.trim().split(/\s+/);
  const completionWords = completion.split(/\s+/);
  
  // Find overlap: how many words at the end of input match start of completion
  let overlapLength = 0;
  for (let i = 1; i <= Math.min(inputWords.length, completionWords.length); i++) {
    const inputEnd = normalize(inputWords.slice(-i).join(' '));
    const completionStart = normalize(completionWords.slice(0, i).join(' '));

    if (inputEnd === completionStart) {
      overlapLength = i;
    }
  }

  // Remove the overlapping words from completion
  if (overlapLength > 0) {
    completion = completionWords.slice(overlapLength).join(' ');
  }
  
  // Strip leading/trailing quotes if present
  completion = completion.replace(/^["']|["']$/g, '');
  
  return completion;
}

//export async function completeLyric(partialLyric: string): Promise<string> {
//  //const prompt = `<|no_think|> You are a lyric autocomplete assistant. Given the partial lyric below, suggest ONLY the next 3-10 words that would naturally continue it. Be concise and creative. Do not repeat the input, do not add explanations, and do not use quotation marks.
//  const prompt = `<｜no_think｜>Continue this lyric naturally. Only give the next few words.
//
//Partial lyric: "${partialLyric}"
//
//Next words:`;
//
//  const response = await client.chat.completions.create({
//    model: MODEL,
//    messages: [{ role: 'user', content: prompt }],
//    max_tokens: 20,
//    temperature: 0.7,
//  });
//
//  let completion = response.choices[0]?.message?.content?.trim() || '';
//  // Remove <think> tags (even if empty)
//  completion = completion.replace(/<\/?think>/gi, '').trim(); 
//  // Strip leading/trailing quotes if present
//  completion = completion.replace(/^["']|["']$/g, '');
//  
//  return completion;
//}