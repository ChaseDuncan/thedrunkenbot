import type { APIRoute } from 'astro';
import { completeLyric } from '../../lib/llm-client';

export const POST: APIRoute = async ({ request }) => {
  try {
    const { partialLyric } = await request.json();

    if (!partialLyric || typeof partialLyric !== 'string') {
      return new Response(
        JSON.stringify({ error: 'Invalid input' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const completion = await completeLyric(partialLyric);

    return new Response(
      JSON.stringify({ completion }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Error completing lyric:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to complete lyric' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};