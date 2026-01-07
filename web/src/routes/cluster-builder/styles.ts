// Item card styles for Cluster Builder

// Items in the current cluster
export const clusterItemClass =
  "border-2 border-primary rounded-lg p-3 text-left bg-primary/5 hover:bg-primary/10 transition-all cursor-pointer";

// Pairwise compatible items that would make a VALID cluster
export const validCandidateClass =
  "border rounded-lg p-4 text-left hover:bg-emerald-50 hover:border-emerald-300 dark:hover:bg-emerald-950/30 dark:hover:border-emerald-800 transition-all cursor-pointer";

// Pairwise compatible items that would make an INVALID cluster
export const invalidCandidateClass =
  "border rounded-lg p-4 text-left hover:bg-amber-50 hover:border-amber-300 dark:hover:bg-amber-950/30 dark:hover:border-amber-800 transition-all cursor-pointer";

// Pairwise incompatible items
export const incompatibleItemClass =
  "border rounded-lg p-3 text-left hover:bg-rose-50 hover:border-rose-300 dark:hover:bg-rose-950/30 dark:hover:border-rose-800 transition-all cursor-pointer opacity-75";
