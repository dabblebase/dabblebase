import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { dabblebase } from "@/utils/dabblebase";
import { api } from "@/utils/trpc/api";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  CheckSquare,
  Edit,
  Loader2,
  Plus,
  SquareCheck,
  Trash2,
} from "lucide-react";
import { GetServerSidePropsContext } from "next";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const CreateTodoSchema = z.object({
  title: z.string().min(1, "Title is required"),
});

const EditTodoSchema = z.object({
  title: z.string().min(1, "Title is required"),
});

export default function HomePage() {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<{
    id: number;
    title: string;
  } | null>(null);

  const utils = api.useUtils();

  const {
    data: todos,
    isLoading: todosLoading,
    error: todosError,
  } = api.todos.getTodoItems.useQuery();

  const createTodoMutation = api.todos.createTodoItem.useMutation({
    onSuccess: () => {
      utils.todos.getTodoItems.invalidate();
      setCreateDialogOpen(false);
      createForm.reset();
      toast.success("Todo created successfully🎉", {
        description: "Your new task has been added to your list.",
        duration: 3000,
      });
    },
    onError: (error) => {
      toast.error("Failed to create todo", {
        description: error.message,
        duration: 5000,
      });
    },
  });

  const toggleTodoMutation = api.todos.toggleTodoItem.useMutation({
    onSuccess: (data) => {
      utils.todos.getTodoItems.invalidate();
      toast.success(
        data.completed ? "Task completed!" : "Task marked as pending...",
        {
          description: data.completed
            ? "Great job on finishing this task!"
            : "Task moved back to your active list.",
          duration: 2000,
        }
      );
    },
    onError: (error) => {
      toast.error("Failed to update todo", {
        description: error.message,
        duration: 5000,
      });
    },
  });

  const updateTodoMutation = api.todos.updateTodoItem.useMutation({
    onSuccess: () => {
      utils.todos.getTodoItems.invalidate();
      setEditDialogOpen(false);
      setEditingTodo(null);
      editForm.reset();
      toast.success("Todo updated successfully!", {
        description: "Your changes have been saved.",
        duration: 3000,
      });
    },
    onError: (error) => {
      toast.error("Failed to update todo", {
        description: error.message,
        duration: 5000,
      });
    },
  });

  const deleteTodoMutation = api.todos.deleteTodoItem.useMutation({
    onSuccess: () => {
      utils.todos.getTodoItems.invalidate();
      toast.success("Todo deleted successfully!", {
        description: "The task has been removed from your list.",
        duration: 3000,
      });
    },
    onError: (error) => {
      toast.error("Failed to delete todo", {
        description: error.message,
        duration: 5000,
      });
    },
  });

  const createForm = useForm<z.infer<typeof CreateTodoSchema>>({
    resolver: zodResolver(CreateTodoSchema),
    defaultValues: {
      title: "",
    },
  });

  const editForm = useForm<z.infer<typeof EditTodoSchema>>({
    resolver: zodResolver(EditTodoSchema),
    defaultValues: {
      title: "",
    },
  });

  const onCreateSubmit = (values: z.infer<typeof CreateTodoSchema>) => {
    createTodoMutation.mutate(values);
  };

  const onEditSubmit = (values: z.infer<typeof EditTodoSchema>) => {
    if (editingTodo) {
      updateTodoMutation.mutate({
        id: editingTodo.id,
        title: values.title,
      });
    }
  };

  const handleToggleTodo = (id: number) => {
    toggleTodoMutation.mutate({ id });
  };

  const handleEditTodo = (todo: { id: number; title: string }) => {
    setEditingTodo(todo);
    editForm.setValue("title", todo.title);
    setEditDialogOpen(true);
  };

  const handleDeleteTodo = (todo: { id: number; title: string }) => {
    deleteTodoMutation.mutate({ id: todo.id });
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Todo App</h1>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Todo
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Create New Todo</DialogTitle>
              <DialogDescription>
                Add a new item to your todo list. What would you like to
                accomplish?
              </DialogDescription>
            </DialogHeader>
            <Form {...createForm}>
              <form
                onSubmit={createForm.handleSubmit(onCreateSubmit)}
                className="space-y-4"
              >
                <FormField
                  control={createForm.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Title</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Enter todo title..."
                          {...field}
                          autoFocus
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline" type="button">
                      Cancel
                    </Button>
                  </DialogClose>
                  <Button type="submit" disabled={createTodoMutation.isPending}>
                    {createTodoMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        Create Todo
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-4">
        {todosLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin mr-2" />
            <p>Loading todos...</p>
          </div>
        )}

        {todosError && (
          <div className="text-center py-8">
            <p className="text-red-500">
              Error loading todos: {todosError.message}
            </p>
          </div>
        )}

        {todos && todos.length === 0 && (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <SquareCheck />
              </EmptyMedia>
              <EmptyTitle>No Todos Yet</EmptyTitle>
              <EmptyDescription>
                You haven&apos;t created any todos yet. Get started by creating
                your first todo.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent>
              <Dialog
                open={createDialogOpen}
                onOpenChange={setCreateDialogOpen}
              >
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Todo
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>Create New Todo</DialogTitle>
                    <DialogDescription>
                      Add a new item to your todo list. What would you like to
                      accomplish?
                    </DialogDescription>
                  </DialogHeader>
                  <Form {...createForm}>
                    <form
                      onSubmit={createForm.handleSubmit(onCreateSubmit)}
                      className="space-y-4"
                    >
                      <FormField
                        control={createForm.control}
                        name="title"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Title</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="Enter todo title..."
                                {...field}
                                autoFocus
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <DialogFooter>
                        <DialogClose asChild>
                          <Button variant="outline" type="button">
                            Cancel
                          </Button>
                        </DialogClose>
                        <Button
                          type="submit"
                          disabled={createTodoMutation.isPending}
                        >
                          {createTodoMutation.isPending ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Creating...
                            </>
                          ) : (
                            <>
                              <Plus className="w-4 h-4 mr-2" />
                              Create Todo
                            </>
                          )}
                        </Button>
                      </DialogFooter>
                    </form>
                  </Form>
                </DialogContent>
              </Dialog>
            </EmptyContent>
          </Empty>
        )}

        {todos && todos.length > 0 && (
          <div className="space-y-2">
            {todos.map((todo) => (
              <Card key={todo.id} className="p-0">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={todo.completed}
                      onCheckedChange={() => handleToggleTodo(todo.id)}
                      disabled={toggleTodoMutation.isPending}
                    />
                    <div className="flex-1">
                      <p
                        className={`${
                          todo.completed
                            ? "line-through text-muted-foreground"
                            : ""
                        }`}
                      >
                        {todo.title}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditTodo(todo)}
                        disabled={updateTodoMutation.isPending}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={deleteTodoMutation.isPending}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Delete Todo</AlertDialogTitle>
                            <AlertDialogDescription>
                              Are you sure you want to delete &ldquo;
                              {todo.title}&rdquo;? This action cannot be undone.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={() => handleDeleteTodo(todo)}
                              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            >
                              {deleteTodoMutation.isPending ? (
                                <>
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                  Deleting...
                                </>
                              ) : (
                                <>
                                  <Trash2 className="w-4 h-4 mr-2" />
                                  Delete
                                </>
                              )}
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Edit Todo Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Todo</DialogTitle>
            <DialogDescription>
              Make changes to your todo item here.
            </DialogDescription>
          </DialogHeader>
          <Form {...editForm}>
            <form
              onSubmit={editForm.handleSubmit(onEditSubmit)}
              className="space-y-4"
            >
              <FormField
                control={editForm.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Enter todo title..."
                        {...field}
                        autoFocus
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="outline" type="button">
                    Cancel
                  </Button>
                </DialogClose>
                <Button type="submit" disabled={updateTodoMutation.isPending}>
                  {updateTodoMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    <>
                      <CheckSquare className="w-4 h-4 mr-2" />
                      Update Todo
                    </>
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  // Verify that the user is signed in
  const { subject, error } = dabblebase.auth.verify(
    context.req.cookies["auth-token"]
  );

  if (error || !subject) {
    // If the user is not authenticated, we will redirect the user
    // back to the homepage so the client never recieves anything
    // from the authenticated-only page.
    console.log(error);
    return {
      redirect: {
        destination: "/authenticate",
        permanent: false,
      },
    };
  }
  return {
    props: {
      subject: subject,
    },
  };
}
