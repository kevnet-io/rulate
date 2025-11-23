// API Client for Rulate backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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
	type: 'string' | 'integer' | 'float' | 'boolean' | 'enum' | 'list';
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
	type: 'exclusion' | 'requirement';
	condition: Record<string, any>;
	enabled?: boolean;
}

export interface Catalog {
	id?: number;
	name: string;
	schema_name: string;
	description?: string;
	metadata?: Record<string, any>;
	created_at?: string;
	updated_at?: string;
}

export interface Item {
	id?: number;
	item_id: string;
	name: string;
	attributes: Record<string, any>;
	metadata?: Record<string, any>;
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

class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE_URL) {
		this.baseUrl = baseUrl;
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<T> {
		const response = await fetch(`${this.baseUrl}${endpoint}`, {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options.headers
			}
		});

		if (!response.ok) {
			const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
			throw new Error(error.detail || `HTTP error! status: ${response.status}`);
		}

		return response.json();
	}

	// Schema endpoints
	async getSchemas(): Promise<Schema[]> {
		return this.request<Schema[]>('/schemas');
	}

	async getSchema(name: string): Promise<Schema> {
		return this.request<Schema>(`/schemas/${name}`);
	}

	async createSchema(schema: Omit<Schema, 'id' | 'created_at' | 'updated_at'>): Promise<Schema> {
		return this.request<Schema>('/schemas', {
			method: 'POST',
			body: JSON.stringify(schema)
		});
	}

	async updateSchema(name: string, schema: Partial<Schema>): Promise<Schema> {
		return this.request<Schema>(`/schemas/${name}`, {
			method: 'PUT',
			body: JSON.stringify(schema)
		});
	}

	async deleteSchema(name: string): Promise<void> {
		await this.request<void>(`/schemas/${name}`, {
			method: 'DELETE'
		});
	}

	// RuleSet endpoints
	async getRuleSets(): Promise<RuleSet[]> {
		return this.request<RuleSet[]>('/rulesets');
	}

	async getRuleSet(name: string): Promise<RuleSet> {
		return this.request<RuleSet>(`/rulesets/${name}`);
	}

	async createRuleSet(ruleset: Omit<RuleSet, 'id' | 'created_at' | 'updated_at'>): Promise<RuleSet> {
		return this.request<RuleSet>('/rulesets', {
			method: 'POST',
			body: JSON.stringify(ruleset)
		});
	}

	async updateRuleSet(name: string, ruleset: Partial<RuleSet>): Promise<RuleSet> {
		return this.request<RuleSet>(`/rulesets/${name}`, {
			method: 'PUT',
			body: JSON.stringify(ruleset)
		});
	}

	async deleteRuleSet(name: string): Promise<void> {
		await this.request<void>(`/rulesets/${name}`, {
			method: 'DELETE'
		});
	}

	// Catalog endpoints
	async getCatalogs(): Promise<Catalog[]> {
		return this.request<Catalog[]>('/catalogs');
	}

	async getCatalog(name: string): Promise<Catalog> {
		return this.request<Catalog>(`/catalogs/${name}`);
	}

	async createCatalog(catalog: Omit<Catalog, 'id' | 'created_at' | 'updated_at'>): Promise<Catalog> {
		return this.request<Catalog>('/catalogs', {
			method: 'POST',
			body: JSON.stringify(catalog)
		});
	}

	async updateCatalog(name: string, catalog: Partial<Catalog>): Promise<Catalog> {
		return this.request<Catalog>(`/catalogs/${name}`, {
			method: 'PUT',
			body: JSON.stringify(catalog)
		});
	}

	async deleteCatalog(name: string): Promise<void> {
		await this.request<void>(`/catalogs/${name}`, {
			method: 'DELETE'
		});
	}

	// Item endpoints
	async getItems(catalogName: string): Promise<Item[]> {
		return this.request<Item[]>(`/catalogs/${catalogName}/items`);
	}

	async getItem(catalogName: string, itemId: string): Promise<Item> {
		return this.request<Item>(`/catalogs/${catalogName}/items/${itemId}`);
	}

	async createItem(catalogName: string, item: Omit<Item, 'id' | 'created_at' | 'updated_at'>): Promise<Item> {
		return this.request<Item>(`/catalogs/${catalogName}/items`, {
			method: 'POST',
			body: JSON.stringify(item)
		});
	}

	async updateItem(catalogName: string, itemId: string, item: Partial<Item>): Promise<Item> {
		return this.request<Item>(`/catalogs/${catalogName}/items/${itemId}`, {
			method: 'PUT',
			body: JSON.stringify(item)
		});
	}

	async deleteItem(catalogName: string, itemId: string): Promise<void> {
		await this.request<void>(`/catalogs/${catalogName}/items/${itemId}`, {
			method: 'DELETE'
		});
	}

	// Evaluation endpoints
	async evaluatePair(
		item1Id: string,
		item2Id: string,
		catalogName: string,
		rulesetName: string
	): Promise<ComparisonResult> {
		return this.request<ComparisonResult>('/evaluate/pair', {
			method: 'POST',
			body: JSON.stringify({
				item1_id: item1Id,
				item2_id: item2Id,
				catalog_name: catalogName,
				ruleset_name: rulesetName
			})
		});
	}

	async evaluateMatrix(
		catalogName: string,
		rulesetName: string
	): Promise<EvaluationMatrix> {
		return this.request<EvaluationMatrix>('/evaluate/matrix', {
			method: 'POST',
			body: JSON.stringify({
				catalog_name: catalogName,
				ruleset_name: rulesetName
			})
		});
	}

	async evaluateItem(
		itemId: string,
		catalogName: string,
		rulesetName: string
	): Promise<ComparisonResult[]> {
		return this.request<ComparisonResult[]>('/evaluate/item', {
			method: 'POST',
			body: JSON.stringify({
				item_id: itemId,
				catalog_name: catalogName,
				ruleset_name: rulesetName
			})
		});
	}
}

// Export a singleton instance
export const api = new ApiClient();
export default api;
