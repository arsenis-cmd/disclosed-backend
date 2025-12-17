export const PROTOCOL_FEE_PERCENT = 7;

export const VERIFICATION_THRESHOLDS = {
  MIN_RELEVANCE: 0.65,
  MIN_NOVELTY: 0.70,
  MIN_COHERENCE: 0.60,
  MIN_COMBINED: 0.60,
};

export const PROOF_LENGTH = {
  MIN: 100,
  MAX: 2000,
  DEFAULT_MIN: 100,
  DEFAULT_MAX: 2000,
};

export const TASK_EXPIRY_HOURS = 24;

export const CONTENT_TYPES = {
  TEXT: 'text',
  VIDEO: 'video',
  IMAGE: 'image',
  URL: 'url',
} as const;
