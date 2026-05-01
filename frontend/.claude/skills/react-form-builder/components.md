# Trace.ai Form Components Reference

## Import Pattern

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form, FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
```

## Form Field Pattern

```tsx
<FormField
  control={form.control}
  name="fieldName"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Field Label</FormLabel>
      <FormControl>
        <Input
          data-test="field-name-input"
          placeholder="Enter value"
          {...field}
        />
      </FormControl>
      <FormDescription>
        Helpful description for the user.
      </FormDescription>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Select Field

```tsx
<FormField
  control={form.control}
  name="category"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Category</FormLabel>
      <Select onValueChange={field.onChange} defaultValue={field.value}>
        <FormControl>
          <SelectTrigger data-test="category-select">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
        </FormControl>
        <SelectContent>
          <SelectItem value="option1">Option 1</SelectItem>
          <SelectItem value="option2">Option 2</SelectItem>
        </SelectContent>
      </Select>
      <FormMessage />
    </FormItem>
  )}
/>
```

## Checkbox Field

```tsx
<FormField
  control={form.control}
  name="acceptTerms"
  render={({ field }) => (
    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
      <FormControl>
        <Checkbox
          data-test="accept-terms-checkbox"
          checked={field.value}
          onCheckedChange={field.onChange}
        />
      </FormControl>
      <div className="space-y-1 leading-none">
        <FormLabel>
          Accept terms and conditions
        </FormLabel>
      </div>
    </FormItem>
  )}
/>
```

## Switch Field

```tsx
<FormField
  control={form.control}
  name="notifications"
  render={({ field }) => (
    <FormItem className="flex items-center justify-between rounded-lg border p-4">
      <div className="space-y-0.5">
        <FormLabel className="text-base">Enable Notifications</FormLabel>
        <FormDescription>
          Receive email notifications for scan results.
        </FormDescription>
      </div>
      <FormControl>
        <Switch
          data-test="notifications-switch"
          checked={field.value}
          onCheckedChange={field.onChange}
        />
      </FormControl>
    </FormItem>
  )}
/>
```

## Submit Button with Loader

```tsx
<Button
  type="submit"
  disabled={mutation.isPending}
  data-test="submit-button"
  className="w-full"
>
  {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {mutation.isPending ? 'Saving...' : 'Save Changes'}
</Button>
```

## Complete Form Template

```tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

import { CreateProjectSchema, type CreateProjectInput } from '../lib/project.schema';
import { useCreateProject } from '../api/use-create-project';

export function ProjectForm() {
  const mutation = useCreateProject();

  const form = useForm<CreateProjectInput>({
    resolver: zodResolver(CreateProjectSchema),
    defaultValues: {
      name: '',
    },
  });

  const onSubmit = (data: CreateProjectInput) => {
    mutation.mutate(data, {
      onSuccess: () => {
        toast.success('Project created successfully');
        form.reset();
      },
      onError: (error) => {
        toast.error(error.message || 'Failed to create project');
      },
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project Name</FormLabel>
              <FormControl>
                <Input data-test="project-name-input" placeholder="My awesome project" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={mutation.isPending} data-test="submit-button">
          {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {mutation.isPending ? 'Creating...' : 'Create Project'}
        </Button>
      </form>
    </Form>
  );
}
```
