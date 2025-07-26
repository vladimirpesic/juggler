<!--
  Svelte Language Test File
  Tests all structural elements supported by the Svelte parser
-->

<script context="module">
  // Module-level code - runs once when the component is first imported
  let moduleCounter = 0;
  
  export function getModuleCounter() {
    return moduleCounter++;
  }
  
  export const MODULE_CONSTANT = "This is a module constant";
  
  // Module-level stores
  import { writable, readable, derived, get } from 'svelte/store';
  
  export const globalStore = writable(0);
  export const moduleStore = readable("module data", (set) => {
    const interval = setInterval(() => {
      set(`module data ${Date.now()}`);
    }, 1000);
    
    return () => clearInterval(interval);
  });
</script>

<script>
  // Component imports
  import { createEventDispatcher, getContext, setContext, tick, beforeUpdate, afterUpdate, onMount, onDestroy } from 'svelte';
  import { spring, tweened } from 'svelte/motion';
  import { fade, fly, slide, scale, draw, crossfade } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import ChildComponent from './ChildComponent.svelte';
  import Button from './ui/Button.svelte';
  
  // TypeScript interface (if using TypeScript)
  interface User {
    id: number;
    name: string;
    email: string;
    isActive: boolean;
  }
  
  interface TodoItem {
    id: string;
    text: string;
    completed: boolean;
    priority: 'low' | 'medium' | 'high';
  }
  
  // Props with types and defaults
  export let title: string = "Default Title";
  export let users: User[] = [];
  export let maxUsers: number = 10;
  export let isVisible: boolean = true;
  export let config: { theme: string; language: string } = { theme: 'dark', language: 'en' };
  export let onUserSelect: (user: User) => void = () => {};
  
  // Internal component state
  let count = 0;
  let inputValue = '';
  let selectedUser: User | null = null;
  let todos: TodoItem[] = [
    { id: '1', text: 'Learn Svelte', completed: false, priority: 'high' },
    { id: '2', text: 'Build an app', completed: false, priority: 'medium' },
    { id: '3', text: 'Deploy to production', completed: false, priority: 'low' }
  ];
  
  // Stores
  const dispatch = createEventDispatcher<{
    userSelected: User;
    countChanged: number;
    todoAdded: TodoItem;
    error: string;
  }>();
  
  const userStore = writable<User[]>(users);
  const selectedStore = writable<User | null>(null);
  const countStore = writable(0);
  
  // Motion stores
  const progress = tweened(0, {
    duration: 400,
    easing: (t) => t * t * t
  });
  
  const coords = spring({ x: 50, y: 50 }, {
    stiffness: 0.1,
    damping: 0.25
  });
  
  // Derived stores
  const activeUsers = derived(
    userStore,
    ($userStore) => $userStore.filter(user => user.isActive)
  );
  
  const completedTodos = derived(
    [todos],
    ([$todos]) => $todos.filter(todo => todo.completed).length
  );
  
  // Context
  const appContext = getContext('app') || {};
  setContext('component', {
    getName: () => 'TestComponent',
    getVersion: () => '1.0.0'
  });
  
  // Reactive declarations
  $: doubledCount = count * 2;
  $: isCountEven = count % 2 === 0;
  $: totalUsers = users.length;
  $: hasUsers = totalUsers > 0;
  $: filteredUsers = users.filter(user => 
    user.name.toLowerCase().includes(inputValue.toLowerCase())
  );
  
  // Complex reactive statement
  $: {
    if (count > 10) {
      console.log('Count is getting high!');
      dispatch('countChanged', count);
    }
  }
  
  // Reactive statement with multiple dependencies
  $: {
    if (selectedUser && users.length > 0) {
      progress.set(users.indexOf(selectedUser) / users.length * 100);
    }
  }
  
  // Functions
  function increment() {
    count += 1;
    countStore.set(count);
  }
  
  function decrement() {
    count = Math.max(0, count - 1);
    countStore.set(count);
  }
  
  function selectUser(user: User) {
    selectedUser = user;
    selectedStore.set(user);
    onUserSelect(user);
    dispatch('userSelected', user);
  }
  
  function addTodo() {
    if (inputValue.trim()) {
      const newTodo: TodoItem = {
        id: Date.now().toString(),
        text: inputValue.trim(),
        completed: false,
        priority: 'medium'
      };
      todos = [...todos, newTodo];
      inputValue = '';
      dispatch('todoAdded', newTodo);
    }
  }
  
  function toggleTodo(id: string) {
    todos = todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    );
  }
  
  function removeTodo(id: string) {
    todos = todos.filter(todo => todo.id !== id);
  }
  
  async function handleAsyncAction() {
    try {
      await tick(); // Wait for DOM updates
      const response = await fetch('/api/data');
      const data = await response.json();
      console.log('Data loaded:', data);
    } catch (error) {
      console.error('Error loading data:', error);
      dispatch('error', error.message);
    }
  }
  
  // Lifecycle functions
  onMount(() => {
    console.log('Component mounted');
    
    // Set up interval
    const interval = setInterval(() => {
      coords.set({
        x: Math.random() * 100,
        y: Math.random() * 100
      });
    }, 2000);
    
    return () => {
      clearInterval(interval);
      console.log('Component cleanup');
    };
  });
  
  onDestroy(() => {
    console.log('Component destroyed');
  });
  
  beforeUpdate(() => {
    console.log('Before update');
  });
  
  afterUpdate(() => {
    console.log('After update');
  });
  
  // Event handlers
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      addTodo();
    } else if (event.key === 'Escape') {
      inputValue = '';
    }
  }
  
  function handleMouseMove(event: MouseEvent) {
    coords.set({
      x: event.clientX / window.innerWidth * 100,
      y: event.clientY / window.innerHeight * 100
    });
  }
  
  // Custom action
  function autofocus(node: HTMLElement) {
    node.focus();
    
    return {
      destroy() {
        // cleanup if needed
      }
    };
  }
  
  // Custom action with parameters
  function tooltip(node: HTMLElement, text: string) {
    const div = document.createElement('div');
    div.textContent = text;
    div.className = 'tooltip';
    
    function handleMouseEnter() {
      document.body.appendChild(div);
    }
    
    function handleMouseLeave() {
      document.body.removeChild(div);
    }
    
    node.addEventListener('mouseenter', handleMouseEnter);
    node.addEventListener('mouseleave', handleMouseLeave);
    
    return {
      update(newText: string) {
        div.textContent = newText;
      },
      destroy() {
        node.removeEventListener('mouseenter', handleMouseEnter);
        node.removeEventListener('mouseleave', handleMouseLeave);
        if (div.parentNode) {
          div.parentNode.removeChild(div);
        }
      }
    };
  }
</script>

<!-- HTML Template -->
<main class="app" class:dark={config.theme === 'dark'} on:mousemove={handleMouseMove}>
  <header>
    <h1 in:fade={{ duration: 300 }}>{title}</h1>
    <p>Module counter: {getModuleCounter()}</p>
    <p>Current count: {count} (doubled: {doubledCount})</p>
    <p class:even={isCountEven} class:odd={!isCountEven}>
      Count is {isCountEven ? 'even' : 'odd'}
    </p>
  </header>

  <!-- Conditional rendering -->
  {#if isVisible}
    <section class="counter" transition:slide>
      <button on:click={decrement} disabled={count === 0}>-</button>
      <span class="count">{count}</span>
      <button on:click={increment}>+</button>
      
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          style="width: {$progress}%"
          transition:scale
        ></div>
      </div>
    </section>
  {/if}

  <!-- Input with two-way binding -->
  <section class="input-section">
    <input
      type="text"
      bind:value={inputValue}
      on:keydown={handleKeydown}
      use:autofocus
      use:tooltip="Type and press Enter to add a todo"
      placeholder="Enter todo item..."
    />
    <Button on:click={addTodo} variant="primary">Add Todo</Button>
  </section>

  <!-- List rendering with animations -->
  <section class="todos">
    <h2>Todos ({todos.length} total, {$completedTodos} completed)</h2>
    
    {#each todos as todo (todo.id)}
      <div 
        class="todo-item" 
        class:completed={todo.completed}
        class:high-priority={todo.priority === 'high'}
        animate:flip={{ duration: 300 }}
        in:fly={{ x: -200, duration: 300 }}
        out:fly={{ x: 200, duration: 300 }}
      >
        <input
          type="checkbox"
          bind:checked={todo.completed}
          on:change={() => toggleTodo(todo.id)}
        />
        <span class="todo-text">{todo.text}</span>
        <span class="priority priority-{todo.priority}">{todo.priority}</span>
        <button 
          class="remove-btn"
          on:click={() => removeTodo(todo.id)}
          use:tooltip="Remove this todo"
        >
          ×
        </button>
      </div>
    {:else}
      <p class="empty-state">No todos yet. Add one above!</p>
    {/each}
  </section>

  <!-- User list with conditional rendering -->
  <section class="users">
    <h2>Users ({totalUsers})</h2>
    
    {#if hasUsers}
      <div class="user-filter">
        <input
          type="text"
          bind:value={inputValue}
          placeholder="Filter users..."
        />
      </div>
      
      <div class="user-list">
        {#each filteredUsers as user, index (user.id)}
          <div 
            class="user-card"
            class:selected={selectedUser?.id === user.id}
            class:inactive={!user.isActive}
            on:click={() => selectUser(user)}
            on:keydown={(e) => e.key === 'Enter' && selectUser(user)}
            role="button"
            tabindex="0"
            animate:flip
            in:fade={{ delay: index * 100 }}
          >
            <h3>{user.name}</h3>
            <p>{user.email}</p>
            <span class="status" class:active={user.isActive}>
              {user.isActive ? 'Active' : 'Inactive'}
            </span>
          </div>
        {:else}
          <p>No users match your filter.</p>
        {/each}
      </div>
    {:else}
      <p class="empty-state">No users available.</p>
    {/if}
  </section>

  <!-- Component composition -->
  <section class="components">
    <ChildComponent 
      bind:value={inputValue}
      {selectedUser}
      on:change={(e) => console.log('Child changed:', e.detail)}
      on:custom={(e) => dispatch('error', e.detail.message)}
      let:childData
    >
      <svelte:fragment slot="header">
        <h3>Child Component Header</h3>
      </svelte:fragment>
      
      <p>Child data: {childData}</p>
      
      <svelte:fragment slot="footer">
        <p>Custom footer content</p>
      </svelte:fragment>
    </ChildComponent>
  </section>

  <!-- Motion and coordinates -->
  <section class="motion">
    <div 
      class="moving-dot"
      style="left: {$coords.x}%; top: {$coords.y}%"
    ></div>
  </section>

  <!-- Async block -->
  <section class="async">
    <button on:click={handleAsyncAction}>Load Async Data</button>
    
    {#await handleAsyncAction()}
      <p>Loading...</p>
    {:then data}
      <p>Data loaded: {JSON.stringify(data)}</p>
    {:catch error}
      <p class="error">Error: {error.message}</p>
    {/await}
  </section>

  <!-- Debug info -->
  {#if process.env.NODE_ENV === 'development'}
    <section class="debug">
      <details>
        <summary>Debug Info</summary>
        <pre>{JSON.stringify({
          count,
          inputValue,
          selectedUser,
          todos: todos.length,
          activeUsers: $activeUsers.length,
          coords: $coords,
          progress: $progress
        }, null, 2)}</pre>
      </details>
    </section>
  {/if}
</main>

<style>
  /* Component styles */
  .app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .app.dark {
    background-color: #1a1a1a;
    color: #ffffff;
  }

  header h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: var(--primary-color, #007acc);
  }

  .counter {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 8px;
  }

  .counter button {
    padding: 0.5rem 1rem;
    font-size: 1.2rem;
    border: none;
    border-radius: 4px;
    background-color: #007acc;
    color: white;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .counter button:hover:not(:disabled) {
    background-color: #005999;
  }

  .counter button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .count {
    font-size: 2rem;
    font-weight: bold;
    min-width: 3rem;
    text-align: center;
  }

  .even {
    color: green;
  }

  .odd {
    color: orange;
  }

  .progress-bar {
    width: 200px;
    height: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background-color: #007acc;
    transition: width 0.3s ease;
  }

  .input-section {
    display: flex;
    gap: 1rem;
    margin: 2rem 0;
  }

  .input-section input {
    flex: 1;
    padding: 0.75rem;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .input-section input:focus {
    outline: none;
    border-color: #007acc;
  }

  .todos {
    margin: 2rem 0;
  }

  .todo-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    margin: 0.5rem 0;
    border: 1px solid #ddd;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .todo-item:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .todo-item.completed {
    opacity: 0.6;
    text-decoration: line-through;
  }

  .todo-item.high-priority {
    border-left: 4px solid #ff4444;
  }

  .todo-text {
    flex: 1;
  }

  .priority {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    text-transform: uppercase;
  }

  .priority-high {
    background-color: #ffebee;
    color: #c62828;
  }

  .priority-medium {
    background-color: #fff3e0;
    color: #ef6c00;
  }

  .priority-low {
    background-color: #e8f5e8;
    color: #2e7d32;
  }

  .remove-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #ff4444;
    padding: 0.25rem;
    border-radius: 4px;
  }

  .remove-btn:hover {
    background-color: #ffebee;
  }

  .users {
    margin: 2rem 0;
  }

  .user-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
  }

  .user-card {
    padding: 1rem;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .user-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  .user-card.selected {
    border-color: #007acc;
    background-color: #f0f8ff;
  }

  .user-card.inactive {
    opacity: 0.6;
  }

  .status.active {
    color: #4caf50;
  }

  .motion {
    position: relative;
    height: 200px;
    border: 2px dashed #ddd;
    border-radius: 8px;
    overflow: hidden;
  }

  .moving-dot {
    position: absolute;
    width: 20px;
    height: 20px;
    background-color: #007acc;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: all 0.3s ease;
  }

  .empty-state {
    text-align: center;
    color: #666;
    font-style: italic;
    padding: 2rem;
  }

  .error {
    color: #ff4444;
    font-weight: bold;
  }

  .debug {
    margin-top: 2rem;
    padding: 1rem;
    background-color: #f5f5f5;
    border-radius: 4px;
  }

  .debug pre {
    font-size: 0.8rem;
    overflow-x: auto;
  }

  /* Global styles */
  :global(.tooltip) {
    position: absolute;
    background-color: #333;
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    pointer-events: none;
    z-index: 1000;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .app {
      padding: 1rem;
    }
    
    .user-list {
      grid-template-columns: 1fr;
    }
    
    .counter {
      flex-wrap: wrap;
      justify-content: center;
    }
  }
</style>
