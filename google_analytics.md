# Google Analytics Event Tracking Implementation Plan

## Overview
This plan outlines how to implement comprehensive Google Analytics 4 (GA4) event tracking for chat requests and tool usage in the FPL Agent application.

## Current State Analysis

### Chat Flow
- Frontend `/api/chat` route processes all chat requests
- Has access to user messages and conversation history  
- Backend streaming events include `tool_call_start`, `tool_call_complete`, and `tool_call_final`
- Tool names and arguments are available from the backend

### Event Tracking Opportunities
- Chat request lifecycle (start, complete, error)
- Tool execution tracking (which tools, success/failure)
- User interaction patterns
- Performance metrics

### Google Analytics Setup
- GA4 is configured via gtag script in `frontend/app/layout.tsx`
- Tracking ID: `G-EKHLEJ070X`

## Implementation Plan

### 1. Create GA4 Helper Module
**File**: `frontend/lib/analytics.ts`
- Utility functions for sending events safely
- Client-side gtag wrapper with error handling
- Type definitions for event parameters
- Privacy-conscious parameter sanitization

### 2. Track Chat Requests
**Location**: `frontend/app/api/chat/route.ts`

**Events to Track**:
- `chat_request_start` - When user sends a message
- `chat_request_complete` - When assistant finishes responding  
- `chat_request_error` - When request fails

**Parameters**:
- `message_length` - Character count of user message
- `conversation_length` - Number of messages in conversation
- `user_id_hash` - Hashed user identifier for privacy
- `response_time` - Time taken for complete response
- `error_type` - Type of error if request fails

### 3. Track Tool Usage
**Location**: Transform stream in `/api/chat/route.ts`

**Events to Track**:
- `tool_call_start` - When tool execution begins
- `tool_call_complete` - When tool execution finishes
- `tool_call_error` - When tool execution fails

**Parameters**:
- `tool_name` - Name of the tool being called (e.g., "search_players", "get_fixtures")
- `execution_time` - Time taken for tool to execute
- `success_status` - Whether tool executed successfully
- `parameters_count` - Number of parameters passed (for complexity measure)
- `result_size` - Approximate size of tool result

### 4. Client-Side Event Integration
**Location**: `frontend/app/assistant.tsx`

**Integration Points**:
- Use existing `onFinish` callback in `useChatRuntime`
- Enhance `MessageMonitor` component to track message events
- Track user interactions (message sent, received)

**Events**:
- `message_sent` - When user sends a message
- `message_received` - When assistant message is displayed
- `conversation_milestone` - At 10, 25, 50, 100 messages

### 5. Event Categories and Structure

#### Chat Events
```javascript
// Chat request initiated
gtag('event', 'chat_request_start', {
  'message_length': 150,
  'conversation_length': 5,
  'user_id_hash': 'abc123...'
});

// Chat request completed
gtag('event', 'chat_request_complete', {
  'response_time': 2500,
  'tools_used': 2,
  'conversation_length': 6
});
```

#### Tool Events
```javascript
// Tool execution
gtag('event', 'tool_call', {
  'tool_name': 'search_players',
  'execution_time': 800,
  'success_status': true,
  'parameters_count': 3
});
```

#### User Interaction Events
```javascript
// Message milestones
gtag('event', 'conversation_milestone', {
  'milestone': 25,
  'session_duration': 1800000
});
```

### 6. Privacy and Data Protection

**User Identification**:
- Hash user IDs using crypto.subtle.digest
- Never send raw Clerk user IDs or email addresses

**Message Content**:
- Track message length/count, not actual content
- Sanitize tool parameters to remove sensitive data

**Parameter Filtering**:
- Remove personally identifiable information
- Limit parameter values to safe, aggregate data

### 7. Implementation Order

1. **Phase 1**: Create analytics helper module
2. **Phase 2**: Add basic chat request tracking
3. **Phase 3**: Implement tool usage tracking  
4. **Phase 4**: Add client-side interaction events
5. **Phase 5**: Test and validate events in GA4 DebugView

### 8. Testing Strategy

**Development Testing**:
- Use GA4 DebugView for real-time event validation
- Test with various tool combinations
- Verify privacy compliance (no PII in events)

**Event Validation**:
- Ensure events fire at correct times
- Validate parameter accuracy
- Check for duplicate events

### 9. Monitoring and Analytics

**Key Metrics to Track**:
- Chat request frequency and patterns
- Most popular tools and their success rates
- User engagement and conversation lengths
- Error rates and failure points
- Performance metrics (response times)

**GA4 Reports**:
- Custom events dashboard
- Tool usage analysis
- User journey mapping
- Performance monitoring

## Technical Considerations

### Client vs Server-Side Tracking
- gtag runs client-side only
- Need to emit events from server to client for API route events
- Consider using custom headers or response metadata

### Error Handling
- Graceful fallback when gtag is unavailable
- Non-blocking event tracking (don't break app if GA fails)
- Logging for debugging without user impact

### Performance Impact
- Minimal impact on chat response times
- Async event tracking
- Batch events where possible