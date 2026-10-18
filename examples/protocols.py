"""Local framing and contract examples, not network protocol implementations.
Run: python protocols.py.
"""
import json
import struct


def encode_message(message):
    body = json.dumps(message, separators=(",", ":")).encode()
    if len(body) > 65536:
        raise ValueError("message too large")
    return struct.pack("!I", len(body)) + body


def take_messages(buffer):
    messages = []
    while len(buffer) >= 4:
        length = struct.unpack("!I", buffer[:4])[0]
        if length > 65536:
            raise ValueError("declared message too large")
        if len(buffer) < length + 4:
            break
        messages.append(json.loads(buffer[4:4 + length]))
        buffer = buffer[4 + length:]
    return messages, buffer


def sse_event(event_id, payload):
    if not isinstance(event_id, int) or event_id < 0:
        raise ValueError("nonnegative integer ID required")
    # JSON escapes embedded newlines, preserving one data field.
    return f"id: {event_id}\ndata: {json.dumps(payload)}\n\n"


def events_after(events, cursor, earliest_retained):
    if cursor < earliest_retained - 1:
        raise ValueError("cursor expired: fetch a new snapshot")
    return [event for event in events if event["id"] > cursor]


def read_order_v2(record):
    # Explicit migration rule: these historical v1 records were INR-only.
    version = record.get("schema_version", 1)
    if version not in (1, 2):
        raise ValueError("unsupported schema version")
    currency = "INR" if version == 1 else record["currency"]
    return {"amount_minor": record["amount_minor"], "currency": currency}


def demo():
    wire = encode_message({"message": "one"}) + encode_message({"message": "two"})
    first, pending = take_messages(wire[:7])
    second, pending = take_messages(pending + wire[7:])
    print("partial read messages:", first)
    print("completed messages:", second, "remaining bytes:", len(pending))
    print("SSE frame:", repr(sse_event(42, {"status": "shipped"})))
    print("reconnect after 1:", events_after([{"id": 1}, {"id": 2}], 1, 1))
    print("old schema adapter:", read_order_v2({"amount_minor": 19900}))


if __name__ == "__main__":
    demo()
