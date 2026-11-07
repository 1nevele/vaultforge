/**
 * Public event envelope and producer-ownership rule (S01-002, S01-004).
 *
 * Event-type ownership is enforced: only an authority receipt establishes
 * authorization, and only the verifier establishes a verified finding (product
 * plan: "enforce event-type ownership"). An event whose authenticated producer
 * does not own its type is rejected, so the scheduler cannot promote its own
 * claim into trusted evidence. Producer identity is set at authenticated
 * ingestion; this schema validates that the (already authenticated) producer is
 * allowed to emit the claimed type.
 */
import { z } from "zod";
import {
  ActorId,
  EventId,
  Generation,
  MissionId,
  OperationId,
  SchemaVersion,
  Sequence,
  Sha256Digest,
  Timestamp,
} from "./common.js";
import { AuthenticatedProducer } from "./producers.js";

/**
 * Which producer class is permitted to emit each public event type. The trusted
 * classes (authority/verifier/supervisor) own the privileged types; scheduler and
 * worker/model own only their observational types.
 */
export const EVENT_TYPE_OWNERS = {
  "actor.started": "supervisor",
  "message.dispatched": "supervisor",
  "tool.dispatch.accepted": "supervisor",
  "execution.observation": "worker",
  "target.discovered": "worker",
  "finding.candidate": "model",
  "finding.verified": "verifier",
  "operation.review.requested": "scheduler",
  "operation.receipt.issued": "authority",
  "operation.denied": "authority",
  "mission.cancellation.requested": "scheduler",
} as const satisfies Record<string, AuthenticatedProducer>;

export type EventType = keyof typeof EVENT_TYPE_OWNERS;

/**
 * Literal tuple of event types. Typed as `[EventType, ...EventType[]]` so the
 * zod enum's inferred value type is the precise `EventType` union rather than
 * widening to `string` — downstream exhaustiveness checks then hold.
 */
export const EVENT_TYPES = Object.keys(EVENT_TYPE_OWNERS) as [
  EventType,
  ...EventType[],
];

export const EventType = z.enum(EVENT_TYPES);

export const EventEnvelope = z
  .object({
    event_id: EventId,
    mission_id: MissionId,
    projection_sequence: Sequence,
    schema_version: SchemaVersion,
    actor_id: ActorId,
    execution_generation: Generation,
    operation_id: OperationId.nullable(),
    authenticated_producer: AuthenticatedProducer,
    event_type: EventType,
    correlation_id: z.string().min(1),
    causation_id: z.string().min(1),
    timestamp: Timestamp,
    payload_reference: Sha256Digest,
  })
  .strict()
  .refine(
    (e) =>
      EVENT_TYPE_OWNERS[e.event_type as EventType] === e.authenticated_producer,
    {
      message:
        "authenticated_producer is not the owner of this event_type",
      path: ["event_type"],
    },
  );
export type EventEnvelope = z.infer<typeof EventEnvelope>;
