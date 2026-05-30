# Claude Code Skills - React Pattern Examples

## Overview
This document contains reusable patterns for implementing Claude Code skills in React applications.

## Pattern 1: Basic Skill Hook

```typescript
import { useCallback, useState } from 'react';

interface SkillResult {
  status: 'success' | 'error' | 'loading';
  data?: any;
  error?: string;
}

export const useSkill = (skillName: string) => {
  const [result, setResult] = useState<SkillResult>({ status: 'loading' });

  const execute = useCallback(async (params: any) => {
    try {
      setResult({ status: 'loading' });
      const response = await fetch(`/api/skills/${skillName}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await response.json();
      setResult({
        status: data.status || 'success',
        data: data.data,
        error: data.error,
      });
    } catch (error) {
      setResult({
        status: 'error',
        error: (error as Error).message,
      });
    }
  }, [skillName]);

  return { ...result, execute };
};
```

## Pattern 2: Skill Component with State

```typescript
import React, { useState } from 'react';
import { useSkill } from './useSkill';

interface Props {
  skillName: string;
  onResult?: (data: any) => void;
}

export const SkillComponent: React.FC<Props> = ({ skillName, onResult }) => {
  const [input, setInput] = useState('');
  const { status, data, error, execute } = useSkill(skillName);

  const handleExecute = async () => {
    await execute({ input });
    if (data) onResult?.(data);
  };

  return (
    <div className="skill-component">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter input..."
      />
      <button onClick={handleExecute} disabled={status === 'loading'}>
        Execute
      </button>
      {status === 'loading' && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
};
```

## Pattern 3: Skill Chain (Orchestrator)

```typescript
export const useSkillChain = () => {
  const [results, setResults] = useState<Record<string, any>>({});

  const executeChain = useCallback(async (skills: Array<{
    name: string;
    params: any;
  }>) => {
    const chainResults: Record<string, any> = {};
    for (const skill of skills) {
      const params = {
        ...skill.params,
        previousResults: chainResults,
      };
      const response = await fetch(`/api/skills/${skill.name}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await response.json();
      chainResults[skill.name] = data;
    }
    setResults(chainResults);
    return chainResults;
  }, []);

  return { results, executeChain };
};
```

## Pattern 4: Error Boundary for Skills

```typescript
import React from 'react';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class SkillErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Skill error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <p>Skill error: {this.state.error?.message}</p>;
    }
    return this.props.children;
  }
}
```

## Pattern 5: Skill Context Provider

```typescript
import React, { createContext, useContext } from 'react';

interface SkillContextType {
  executeSkill: (name: string, params: any) => Promise<any>;
  getSkillStatus: (name: string) => string;
}

const SkillContext = createContext<SkillContextType | undefined>(undefined);

export const SkillProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const executeSkill = async (name: string, params: any) => {
    const response = await fetch(`/api/skills/${name}`, {
      method: 'POST',
      body: JSON.stringify(params),
    });
    return response.json();
  };

  const getSkillStatus = (name: string) => {
    // Implement status tracking
    return 'ready';
  };

  return (
    <SkillContext.Provider value={{ executeSkill, getSkillStatus }}>
      {children}
    </SkillContext.Provider>
  );
};

export const useSkillContext = () => {
  const context = useContext(SkillContext);
  if (!context) throw new Error('useSkillContext must be used within SkillProvider');
  return context;
};
```

## Best Practices
1. **Error Handling**: Always wrap skills in try-catch blocks
2. **Loading States**: Show loading indicators during execution
3. **Result Validation**: Validate skill outputs before using
4. **State Management**: Use hooks for local state, context for global
5. **Performance**: Memoize skill callbacks to prevent unnecessary re-renders
6. **Testing**: Test skills with mock data
7. **Types**: Use TypeScript for type safety
