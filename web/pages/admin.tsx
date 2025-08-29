import AdminLayout from "@/components/admin/admin-layout";
import { adminUserListColumsGenerator } from "@/components/admin/user-table/columns";
import { DataTable } from "@/components/ui/data-table";
import { useAddInstructor } from "@/hooks/api/admin/use-add-instructor";
import { useListUsers } from "@/hooks/api/admin/use-list-users";
import { useRemoveInstructor } from "@/hooks/api/admin/use-remove-instructor";
import { fetchClient } from "@/utils/api";
import { GetServerSidePropsContext } from "next";
import { toast } from "sonner";

export default function AdminPage() {
  const { usersData } = useListUsers();
  const { addInstructor, refetchOnSuccess: refetchOnAddInstructorSuccess } =
    useAddInstructor();
  const {
    removeInstructor,
    refetchOnSuccess: refetchOnRemoveInstructorSuccess,
  } = useRemoveInstructor();

  const addInstructorAction = (userId: number) => {
    addInstructor(
      {
        body: {
          id: userId,
        },
      },
      {
        onSuccess: () => {
          refetchOnAddInstructorSuccess();
          toast.success("Successfully added instructor role.");
        },
        onError: () => {
          toast.error("Failed to add instructor role.", {
            description: "Please try again later.",
          });
        },
      }
    );
  };

  const removeInstructorAction = (userId: number) => {
    removeInstructor(
      {
        body: {
          id: userId,
        },
      },
      {
        onSuccess: () => {
          refetchOnRemoveInstructorSuccess();
          toast.success("Successfully removed instructor role.");
        },
        onError: () => {
          toast.error("Failed to remove instructor role.", {
            description: "Please try again later.",
          });
        },
      }
    );
  };

  return (
    <div className="flex flex-col mx-auto w-full max-w-[1200px] px-4 gap-8 my-8">
      <h1 className="text-2xl font-semibold">Admin Portal</h1>
      {!!usersData && (
        <DataTable
          columns={adminUserListColumsGenerator(
            addInstructorAction,
            removeInstructorAction
          )}
          data={usersData.users}
        />
      )}
    </div>
  );
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  // Check if the user is an admin
  const { data: adminData, error: adminError } = await fetchClient.GET(
    "/api/admin/",
    {
      headers: {
        Cookie: context.req.headers.cookie || "",
      },
    }
  );

  console.log(adminData, adminError);

  if (adminError || !adminData) {
    return {
      redirect: {
        destination: `/`,
        permanent: false,
      },
    };
  } else {
    return { props: {} };
  }
}

AdminPage.getLayout = function getLayout(page: React.ReactNode) {
  return <AdminLayout>{page}</AdminLayout>;
};
