

export const maxDuration = 30;

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
  try {
    // Get the token from the Authorization header (sent by client)
    const authHeader = req.headers.get('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Authorization header required' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    if (!token) {
      return new Response(JSON.stringify({ error: 'JWT token required' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const { messages } = await req.json();
    
    // Get the latest message from the user and extract text properly
    const latestMessage = messages[messages.length - 1];
    let userMessageText = "";
    
    if (typeof latestMessage?.content === "string") {
      userMessageText = latestMessage.content;
    } else if (Array.isArray(latestMessage?.content)) {
      // Extract text from content array format
      userMessageText = latestMessage.content
        .filter((part: { type: string }) => part.type === "text")
        .map((part: { text: string }) => part.text)
        .join(" ");
    }
    
    // Prepare conversation history (exclude the latest message as it's sent separately)
    const conversationHistory = messages.slice(0, -1).map((msg: { role: string; content: string }) => ({
      role: msg.role,
      content: msg.content
    }));

    // Call our Python backend with auth token
    console.log('Calling backend with token:', `Bearer ${token.substring(0, 20)}...`);
    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({
        message: [{ type: "text", text: userMessageText }],
        conversation_history: conversationHistory,
        context: {}
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    // Create a transform stream to convert backend events to assistant-ui format
    const activeCalls = new Map(); // Track active tool calls
    let lineBuffer = ''; // Buffer for partial lines across chunks

    const transformStream = new TransformStream({
      transform(chunk, controller) {
        const decoder = new TextDecoder();
        const text = decoder.decode(chunk);

        // Prepend any buffered partial line from previous chunk
        const data = lineBuffer + text;
        lineBuffer = '';

        // Split by lines to handle multiple events in one chunk
        const lines = data.split('\n');

        // Last element may be a partial line (if chunk didn't end with \n)
        // Buffer it for the next chunk
        if (!data.endsWith('\n')) {
          lineBuffer = lines.pop() || '';
        }

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          if (trimmed.startsWith('0:')) {
            try {
              const eventData = JSON.parse(trimmed.slice(2));

              switch (eventData.type) {
                case 'tool_call_start':
                  // Store tool call for later completion
                  activeCalls.set(eventData.tool_call_id, {
                    name: eventData.tool_name,
                    arguments: eventData.tool_arguments
                  });
                  // Don't send anything yet, wait for completion
                  break;

                case 'tool_call_complete':
                case 'tool_call_final':
                  // Send complete tool call information as a single message part
                  const toolCall = activeCalls.get(eventData.tool_call_id);
                  if (toolCall) {
                    // Always send tool calls as cards first
                    const toolCallData = {
                      name: toolCall.name,
                      arguments: toolCall.arguments,
                      result: eventData.result
                    };

                    const specialText = `__TOOL_CALL__:${JSON.stringify(toolCallData)}`;
                    controller.enqueue(new TextEncoder().encode(`0:${JSON.stringify(specialText)}\n`));

                    activeCalls.delete(eventData.tool_call_id);
                  }
                  break;

                case 'text':
                  // Forward text chunks directly
                  controller.enqueue(new TextEncoder().encode(`0:${JSON.stringify(eventData.content)}\n`));
                  break;

                case 'final_answer':
                case 'final_result':
                  // Skip final answer events - the text chunks already contain the streaming content
                  break;

                default:
                  // Skip unknown event types
                  console.log('Unknown event type:', eventData.type);
                  break;
              }
            } catch (e) {
              console.error('Failed to parse event:', trimmed, e);
              // Don't forward raw chunks - they'd corrupt the Data Stream Protocol
            }
          } else if (trimmed === 'd:') {
            // Forward end-of-stream marker with proper JSON value
            controller.enqueue(new TextEncoder().encode(`d:{"finishReason":"stop"}\n`));
          }
        }
      }
    });

    // Pipe the backend response through our transform stream
    const transformedStream = response.body?.pipeThrough(transformStream);

    return new Response(transformedStream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error("Error calling backend:", error);
    
    // Return a proper error stream
    const errorStream = new ReadableStream({
      start(controller) {
        const errorText = "I'm sorry, I encountered an error while processing your request. Please make sure the backend server is running.";
        controller.enqueue(new TextEncoder().encode(`0:${JSON.stringify(errorText)}\n`));
        controller.enqueue(new TextEncoder().encode(`d:{"finishReason":"stop"}\n`));
        controller.close();
      }
    });
    
    return new Response(errorStream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  }
}
