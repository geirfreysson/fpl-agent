export async function GET() {
  try {
    const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
    
    // Check if backend is healthy
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout to prevent hanging
      signal: AbortSignal.timeout(5000)
    });

    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.status}`);
    }

    const backendHealth = await response.json();
    
    return Response.json({
      status: "healthy",
      frontend: "ok", 
      backend: backendHealth,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Health check failed:', error);
    
    return Response.json({
      status: "unhealthy",
      frontend: "ok",
      backend: "failed",
      error: error instanceof Error ? error.message : "Unknown error",
      timestamp: new Date().toISOString()
    }, { status: 503 });
  }
}