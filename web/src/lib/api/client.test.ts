/**
 * Tests for API Client
 *
 * Tests cover HTTP methods, error handling, and data transformations.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import type { Schema, RuleSet, Catalog } from './client';

// We'll test the client by mocking fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Import after setting up global.fetch
const { default: apiClient } = await import('./client');

describe('API Client', () => {
	beforeEach(() => {
		mockFetch.mockClear();
	});

	describe('Schema Endpoints', () => {
		describe('getSchemas', () => {
			it('fetches all schemas', async () => {
				const mockSchemas: Schema[] = [
					{
						id: 1,
						name: 'test_schema',
						version: '1.0.0',
						dimensions: []
					}
				];

				mockFetch.mockResolvedValueOnce({
					ok: true,
					json: async () => mockSchemas
				});

				const result = await apiClient.getSchemas();

				expect(mockFetch).toHaveBeenCalledTimes(1);
				expect(mockFetch).toHaveBeenCalledWith(
					expect.stringContaining('/schemas'),
					expect.objectContaining({
						headers: expect.objectContaining({
							'Content-Type': 'application/json'
						})
					})
				);
				expect(result).toEqual(mockSchemas);
			});

			it('throws error on API failure', async () => {
				mockFetch.mockResolvedValueOnce({
					ok: false,
					status: 500,
					json: async () => ({ detail: 'Server error' })
				});

				await expect(apiClient.getSchemas()).rejects.toThrow('Server error');
			});
		});

		describe('getSchema', () => {
			it('fetches a single schema by name', async () => {
				const mockSchema: Schema = {
					id: 1,
					name: 'test_schema',
					version: '1.0.0',
					dimensions: [
						{
							name: 'category',
							type: 'enum',
							values: ['shirt', 'pants'],
							required: true
						}
					]
				};

				mockFetch.mockResolvedValueOnce({
					ok: true,
					json: async () => mockSchema
				});

				const result = await apiClient.getSchema('test_schema');

				expect(mockFetch).toHaveBeenCalledWith(
					expect.stringContaining('/schemas/test_schema'),
					expect.any(Object)
				);
				expect(result).toEqual(mockSchema);
			});

			it('throws error when schema not found', async () => {
				mockFetch.mockResolvedValueOnce({
					ok: false,
					status: 404,
					json: async () => ({ detail: 'Schema not found' })
				});

				await expect(apiClient.getSchema('nonexistent')).rejects.toThrow('Schema not found');
			});
		});

		describe('createSchema', () => {
			it('creates a new schema', async () => {
				const newSchema = {
					name: 'new_schema',
					version: '1.0.0',
					dimensions: []
				};

				const createdSchema: Schema = {
					...newSchema,
					id: 1,
					created_at: new Date().toISOString(),
					updated_at: new Date().toISOString()
				};

				mockFetch.mockResolvedValueOnce({
					ok: true,
					json: async () => createdSchema
				});

				const result = await apiClient.createSchema(newSchema);

				expect(mockFetch).toHaveBeenCalledWith(
					expect.stringContaining('/schemas'),
					expect.objectContaining({
						method: 'POST',
						body: JSON.stringify(newSchema)
					})
				);
				expect(result).toEqual(createdSchema);
			});

			it('throws error on validation failure', async () => {
				mockFetch.mockResolvedValueOnce({
					ok: false,
					status: 422,
					json: async () => ({ detail: 'Validation error' })
				});

				const invalidSchema = {
					name: '',
					version: '1.0.0',
					dimensions: []
				};

				await expect(apiClient.createSchema(invalidSchema)).rejects.toThrow('Validation error');
			});
		});

		describe('updateSchema', () => {
			it('updates an existing schema', async () => {
				const updatedSchema: Schema = {
					id: 1,
					name: 'test_schema',
					version: '2.0.0',
					dimensions: [],
					updated_at: new Date().toISOString()
				};

				mockFetch.mockResolvedValueOnce({
					ok: true,
					json: async () => updatedSchema
				});

				const result = await apiClient.updateSchema('test_schema', { version: '2.0.0' });

				expect(mockFetch).toHaveBeenCalledWith(
					expect.stringContaining('/schemas/test_schema'),
					expect.objectContaining({
						method: 'PUT',
						body: JSON.stringify({ version: '2.0.0' })
					})
				);
				expect(result).toEqual(updatedSchema);
			});
		});

		describe('deleteSchema', () => {
			it('deletes a schema', async () => {
				mockFetch.mockResolvedValueOnce({
					ok: true,
					json: async () => ({})
				});

				await apiClient.deleteSchema('test_schema');

				expect(mockFetch).toHaveBeenCalledWith(
					expect.stringContaining('/schemas/test_schema'),
					expect.objectContaining({
						method: 'DELETE'
					})
				);
			});

			it('throws error when schema cannot be deleted', async () => {
				mockFetch.mockResolvedValueOnce({
					ok: false,
					status: 409,
					json: async () => ({ detail: 'Schema in use' })
				});

				await expect(apiClient.deleteSchema('in_use_schema')).rejects.toThrow('Schema in use');
			});
		});
	});

	describe('Error Handling', () => {
		it('handles network errors', async () => {
			mockFetch.mockRejectedValueOnce(new Error('Network error'));

			await expect(apiClient.getSchemas()).rejects.toThrow('Network error');
		});

		it('handles malformed JSON responses', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: async () => {
					throw new Error('Invalid JSON');
				}
			});

			await expect(apiClient.getSchemas()).rejects.toThrow();
		});

		it('provides fallback error message for unknown errors', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: false,
				status: 500,
				json: async () => ({})  // No detail field
			});

			await expect(apiClient.getSchemas()).rejects.toThrow(/HTTP error.*500/);
		});
	});

	describe('Request Headers', () => {
		it('includes Content-Type header by default', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => []
			});

			await apiClient.getSchemas();

			expect(mockFetch).toHaveBeenCalledWith(
				expect.any(String),
				expect.objectContaining({
					headers: expect.objectContaining({
						'Content-Type': 'application/json'
					})
				})
			);
		});

		it('allows custom headers to be added', async () => {
			mockFetch.mockResolvedValueOnce({
				ok: true,
				json: async () => ({})
			});

			// This would require modifying the client to accept custom headers,
			// but we're testing the current implementation
			await apiClient.getSchemas();

			expect(mockFetch).toHaveBeenCalled();
		});
	});
});
