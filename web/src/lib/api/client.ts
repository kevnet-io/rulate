// API Client for Rulate backend
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV
    ? "http://localhost:8000/api/v1" // Dev: separate servers
    : "/api/v1"); // Prod: same origin

export interface Schema {
  id?: number;
  name: string;
  version: string;
  dimensions: Dimension[];
  created_at?: string;
  updated_at?: string;
}

export interface Dimension {
  name: string;
  type: "string" | "integer" | "float" | "boolean" | "enum" | "list";
  required?: boolean;
  values?: string[];
  min?: number;
  max?: number;
  item_type?: string;
}

export interface RuleSet {
  id?: number;
  name: string;
  version: string;
  schema_name: string;
  rules: Rule[];
  created_at?: string;
  updated_at?: string;
}

export interface Rule {
  name: string;
  type: "exclusion" | "requirement";
  condition: Record<string, unknown>;
  enabled?: boolean;
}

export interface Catalog {
  id?: number;
  name: string;
  schema_name: string;
  description?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface Item {
  id?: number;
  item_id: string;
  name: string;
  attributes: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface ComparisonResult {
  item1_id: string;
  item2_id: string;
  compatible: boolean;
  rules_evaluated: RuleEvaluation[];
  evaluated_at: string;
}

export interface RuleEvaluation {
  rule_name: string;
  passed: boolean;
  reason: string;
}

export interface EvaluationMatrix {
  catalog_name: string;
  ruleset_name: string;
  results: ComparisonResult[];
  total_comparisons: number;
  compatible_count: number;
  compatibility_rate: number;
}

export interface ClusterRule {
  name: string;
  type: "exclusion" | "requirement";
  condition: Record<string, unknown>;
  enabled?: boolean;
  description?: string;
}

export interface ClusterRuleSet {
  id?: number;
  name: string;
  version: string;
  schema_ref?: string; // For creating
  schema_name?: string; // From API response
  pairwise_ruleset_ref?: string; // For creating
  pairwise_ruleset_name?: string; // From API response
  rules: ClusterRule[];
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Cluster {
  id: string;
  item_ids: string[];
  size: number;
  is_maximal: boolean;
  is_maximum: boolean;
  rule_evaluations: RuleEvaluation[];
  metadata: Record<string, unknown>;
}

export interface ClusterRelationship {
  cluster_id: string;
  related_cluster_id: string;
  relationship_type: "subset" | "superset" | "overlapping";
  shared_items: string[];
  overlap_size: number;
}

// Cluster Builder types
export interface ValidateClusterRequest {
  catalog_name: string;
  cluster_ruleset_name: string;
  item_ids: string[];
}

export interface ValidateClusterResponse {
  item_ids: string[];
  is_valid: boolean;
  rule_evaluations: RuleEvaluation[];
}

export interface CandidateResult {
  item_id: string;
  is_pairwise_compatible: boolean;
  cluster_if_added: ValidateClusterResponse;
}

export interface EvaluateCandidatesRequest {
  catalog_name: string;
  pairwise_ruleset_name: string;
  cluster_ruleset_name: string;
  base_item_ids: string[];
  candidate_item_ids?: string[];
}

export interface EvaluateCandidatesResponse {
  base_validation: ValidateClusterResponse;
  candidates: CandidateResult[];
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Schema endpoints
  async getSchemas(): Promise<Schema[]> {
    return this.request<Schema[]>("/schemas");
  }

  async getSchema(name: string): Promise<Schema> {
    return this.request<Schema>(`/schemas/${name}`);
  }

  async createSchema(
    schema: Omit<Schema, "id" | "created_at" | "updated_at">,
  ): Promise<Schema> {
    return this.request<Schema>("/schemas", {
      method: "POST",
      body: JSON.stringify(schema),
    });
  }

  async updateSchema(name: string, schema: Partial<Schema>): Promise<Schema> {
    return this.request<Schema>(`/schemas/${name}`, {
      method: "PUT",
      body: JSON.stringify(schema),
    });
  }

  async deleteSchema(name: string): Promise<void> {
    await this.request<void>(`/schemas/${name}`, {
      method: "DELETE",
    });
  }

  // RuleSet endpoints
  async getRuleSets(): Promise<RuleSet[]> {
    return this.request<RuleSet[]>("/rulesets");
  }

  async getRuleSet(name: string): Promise<RuleSet> {
    return this.request<RuleSet>(`/rulesets/${name}`);
  }

  async createRuleSet(
    ruleset: Omit<RuleSet, "id" | "created_at" | "updated_at">,
  ): Promise<RuleSet> {
    return this.request<RuleSet>("/rulesets", {
      method: "POST",
      body: JSON.stringify(ruleset),
    });
  }

  async updateRuleSet(
    name: string,
    ruleset: Partial<RuleSet>,
  ): Promise<RuleSet> {
    return this.request<RuleSet>(`/rulesets/${name}`, {
      method: "PUT",
      body: JSON.stringify(ruleset),
    });
  }

  async deleteRuleSet(name: string): Promise<void> {
    await this.request<void>(`/rulesets/${name}`, {
      method: "DELETE",
    });
  }

  // Catalog endpoints
  async getCatalogs(): Promise<Catalog[]> {
    return this.request<Catalog[]>("/catalogs");
  }

  async getCatalog(name: string): Promise<Catalog> {
    return this.request<Catalog>(`/catalogs/${name}`);
  }

  async createCatalog(
    catalog: Omit<Catalog, "id" | "created_at" | "updated_at">,
  ): Promise<Catalog> {
    return this.request<Catalog>("/catalogs", {
      method: "POST",
      body: JSON.stringify(catalog),
    });
  }

  async updateCatalog(
    name: string,
    catalog: Partial<Catalog>,
  ): Promise<Catalog> {
    return this.request<Catalog>(`/catalogs/${name}`, {
      method: "PUT",
      body: JSON.stringify(catalog),
    });
  }

  async deleteCatalog(name: string): Promise<void> {
    await this.request<void>(`/catalogs/${name}`, {
      method: "DELETE",
    });
  }

  // Item endpoints
  async getItems(catalogName: string): Promise<Item[]> {
    return this.request<Item[]>(`/catalogs/${catalogName}/items`);
  }

  async getItem(catalogName: string, itemId: string): Promise<Item> {
    return this.request<Item>(`/catalogs/${catalogName}/items/${itemId}`);
  }

  async createItem(
    catalogName: string,
    item: Omit<Item, "id" | "created_at" | "updated_at">,
  ): Promise<Item> {
    return this.request<Item>(`/catalogs/${catalogName}/items`, {
      method: "POST",
      body: JSON.stringify(item),
    });
  }

  async updateItem(
    catalogName: string,
    itemId: string,
    item: Partial<Item>,
  ): Promise<Item> {
    return this.request<Item>(`/catalogs/${catalogName}/items/${itemId}`, {
      method: "PUT",
      body: JSON.stringify(item),
    });
  }

  async deleteItem(catalogName: string, itemId: string): Promise<void> {
    await this.request<void>(`/catalogs/${catalogName}/items/${itemId}`, {
      method: "DELETE",
    });
  }

  // ClusterRuleSet endpoints
  async getClusterRuleSets(): Promise<ClusterRuleSet[]> {
    return this.request<ClusterRuleSet[]>("/cluster-rulesets");
  }

  async getClusterRuleSet(name: string): Promise<ClusterRuleSet> {
    return this.request<ClusterRuleSet>(`/cluster-rulesets/${name}`);
  }

  async createClusterRuleSet(
    clusterRuleset: Omit<ClusterRuleSet, "id" | "created_at" | "updated_at">,
  ): Promise<ClusterRuleSet> {
    return this.request<ClusterRuleSet>("/cluster-rulesets", {
      method: "POST",
      body: JSON.stringify({
        name: clusterRuleset.name,
        version: clusterRuleset.version,
        description: clusterRuleset.description,
        schema_name: clusterRuleset.schema_ref,
        pairwise_ruleset_name: clusterRuleset.pairwise_ruleset_ref,
        rules: clusterRuleset.rules,
      }),
    });
  }

  async updateClusterRuleSet(
    name: string,
    clusterRuleset: Partial<ClusterRuleSet>,
  ): Promise<ClusterRuleSet> {
    return this.request<ClusterRuleSet>(`/cluster-rulesets/${name}`, {
      method: "PUT",
      body: JSON.stringify(clusterRuleset),
    });
  }

  async deleteClusterRuleSet(name: string): Promise<void> {
    await this.request<void>(`/cluster-rulesets/${name}`, {
      method: "DELETE",
    });
  }

  // Evaluation endpoints
  async evaluatePair(
    item1Id: string,
    item2Id: string,
    catalogName: string,
    rulesetName: string,
  ): Promise<ComparisonResult> {
    return this.request<ComparisonResult>("/evaluate/pair", {
      method: "POST",
      body: JSON.stringify({
        item1_id: item1Id,
        item2_id: item2Id,
        catalog_name: catalogName,
        ruleset_name: rulesetName,
      }),
    });
  }

  async evaluateMatrix(
    catalogName: string,
    rulesetName: string,
  ): Promise<EvaluationMatrix> {
    return this.request<EvaluationMatrix>("/evaluate/matrix", {
      method: "POST",
      body: JSON.stringify({
        catalog_name: catalogName,
        ruleset_name: rulesetName,
      }),
    });
  }

  async evaluateItem(
    itemId: string,
    catalogName: string,
    rulesetName: string,
  ): Promise<ComparisonResult[]> {
    return this.request<ComparisonResult[]>("/evaluate/item", {
      method: "POST",
      body: JSON.stringify({
        item_id: itemId,
        catalog_name: catalogName,
        ruleset_name: rulesetName,
      }),
    });
  }

  // Cluster Builder endpoints
  async validateCluster(
    catalogName: string,
    pairwiseRulesetName: string,
    clusterRulesetName: string,
    itemIds: string[],
  ): Promise<ValidateClusterResponse> {
    return this.request<ValidateClusterResponse>("/evaluate/cluster/validate", {
      method: "POST",
      body: JSON.stringify({
        catalog_name: catalogName,
        pairwise_ruleset_name: pairwiseRulesetName,
        cluster_ruleset_name: clusterRulesetName,
        item_ids: itemIds,
      }),
    });
  }

  async evaluateCandidates(
    catalogName: string,
    pairwiseRulesetName: string,
    clusterRulesetName: string,
    baseItemIds: string[],
    candidateItemIds?: string[],
  ): Promise<EvaluateCandidatesResponse> {
    return this.request<EvaluateCandidatesResponse>(
      "/evaluate/cluster/candidates",
      {
        method: "POST",
        body: JSON.stringify({
          catalog_name: catalogName,
          pairwise_ruleset_name: pairwiseRulesetName,
          cluster_ruleset_name: clusterRulesetName,
          base_item_ids: baseItemIds,
          candidate_item_ids: candidateItemIds,
        }),
      },
    );
  }

  // Export endpoints
  async exportSchemas(): Promise<unknown[]> {
    return this.request<unknown[]>("/export/schemas");
  }

  async exportSchema(name: string): Promise<unknown> {
    return this.request<unknown>(`/export/schemas/${name}`);
  }

  async exportRuleSets(): Promise<unknown[]> {
    return this.request<unknown[]>("/export/rulesets");
  }

  async exportRuleSet(name: string): Promise<unknown> {
    return this.request<unknown>(`/export/rulesets/${name}`);
  }

  async exportClusterRuleSets(): Promise<unknown[]> {
    return this.request<unknown[]>("/export/cluster-rulesets");
  }

  async exportClusterRuleSet(name: string): Promise<unknown> {
    return this.request<unknown>(`/export/cluster-rulesets/${name}`);
  }

  async exportCatalog(name: string): Promise<unknown> {
    return this.request<unknown>(`/export/catalogs/${name}`);
  }

  async exportCatalogs(): Promise<unknown[]> {
    return this.request<unknown[]>("/export/catalogs");
  }

  async exportAll(): Promise<unknown> {
    return this.request<unknown>("/export/all");
  }

  // Import endpoints
  async importSchemas(
    schemas: unknown[],
    skipExisting: boolean = false,
  ): Promise<{ message: string; detail?: string }> {
    return this.request<{ message: string; detail?: string }>(
      `/import/schemas?skip_existing=${skipExisting}`,
      {
        method: "POST",
        body: JSON.stringify(schemas),
      },
    );
  }

  async importRuleSets(
    rulesets: unknown[],
    skipExisting: boolean = false,
  ): Promise<{ message: string; detail?: string }> {
    return this.request<{ message: string; detail?: string }>(
      `/import/rulesets?skip_existing=${skipExisting}`,
      {
        method: "POST",
        body: JSON.stringify(rulesets),
      },
    );
  }

  async importClusterRuleSets(
    clusterRulesets: unknown[],
    skipExisting: boolean = false,
  ): Promise<{ message: string; detail?: string }> {
    return this.request<{ message: string; detail?: string }>(
      `/import/cluster-rulesets?skip_existing=${skipExisting}`,
      {
        method: "POST",
        body: JSON.stringify(clusterRulesets),
      },
    );
  }

  async importCatalogs(
    catalogs: unknown[],
    skipExisting: boolean = false,
  ): Promise<{ message: string; detail?: string }> {
    return this.request<{ message: string; detail?: string }>(
      `/import/catalogs?skip_existing=${skipExisting}`,
      {
        method: "POST",
        body: JSON.stringify(catalogs),
      },
    );
  }

  async importAll(
    data: unknown,
    skipExisting: boolean = false,
  ): Promise<{ message: string; detail?: string }> {
    return this.request<{ message: string; detail?: string }>(
      `/import/all?skip_existing=${skipExisting}`,
      {
        method: "POST",
        body: JSON.stringify(data),
      },
    );
  }
}

// Export a singleton instance
export const api = new ApiClient();
export default api;
