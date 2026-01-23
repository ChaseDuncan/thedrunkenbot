import type { APIRoute } from 'astro';

const BACKEND_URL = import.meta.env.BACKEND_URL || 'http://localhost:8001';

export const POST: APIRoute = async ({ request }) => {
  try {
    const { partialLyric } = await request.json();

    if (!partialLyric || typeof partialLyric !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Invalid input' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    console.log('Calling backend:', `${BACKEND_URL}/complete`);
    console.log('Payload:', { text: partialLyric });

    // Forward to FastAPI backend
    const response = await fetch(`${BACKEND_URL}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: partialLyric, max_tokens: 10, temperature: 1.0 }),
    });

    console.log('Backend response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      
      let errorDetail;
      try {
        const errorJson = JSON.parse(errorText);
        errorDetail = errorJson.detail || errorJson.message || 'Backend error';
      } catch {
        errorDetail = errorText || 'Backend error';
      }
      
      throw new Error(errorDetail);
    }

    const data = await response.json();
    console.log('Backend response data:', data);

    return new Response(
      JSON.stringify({ completion: data.completion }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Error completing lyric:', error);
    console.error('Error details:', error instanceof Error ? error.message : error);
    
    return new Response(
      JSON.stringify({ 
        error: error instanceof Error ? error.message : 'Failed to complete lyric' 
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};