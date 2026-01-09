from invoke import Context
from pathlib import Path

## Some older version of python don't like the self-referential annotation. This is a work-around.
class JobBase:
    ...
    
class JobBase:
    """
    If you want to implement your own job type, create a subclass based on this one.
    
    The only functions you should override are `__init__`, `run`, and optionally `needs_to_run`. 
    See the documentation of each function for more information.
    """
    # Class
    _resolved_jobs: list[JobBase] = []
    
    @classmethod
    def get_all_resolved_mod_outputs(cls) -> dict[Path, Path]:
        """Get the combined mod_output_files from all previously run jobs, regardless of dependency.

        Returns:
            dict[Path, Path]: The combined mod_output_files. The key will be the desired file location in the output, the value will be the path in the project.
        """
        retVal = {}
        for i in cls._resolved_jobs:
            retVal.update(i.mod_output_files)
        
        return retVal
    
    # Instance:
    _has_been_resolved: bool
    no_duplication: bool
    dependencies: list[JobBase]
    mod_output_files: dict[Path, Path]
    
    # Overridable Functions:
    def __init__(self):
        """
        Base initializer for jobs. Overridable for new job types.
        
        When you override this method, be sure to call super().__init__() to initialize parent class attribute.
        """
        self._has_been_resolved = False
        self.no_duplication = True
        self.dependencies = []
        self.mod_output_files = {}
    

    def needs_to_run(self, c: Context) -> bool:
        """Checks if the current job needs to be run. Optionally override when defining your own job type.
        
        The default implementation always returns `True`, meaning that the job should always be run
        (useful when checking is actually harder than running, such as with invoking Make or CMake).
        
        Be advised that if a job doesn't need to be run, its dependency jobs will not be resolved.
        
        You should not call `run` from this method.

        Args:
            c (Context): The pyinvoke Context from the current task invokation.

        Returns:
            bool: True if the job needs to be run. False if otherwise.
        """
        return True
    
    def run(self, c: Context):
        """This function defines the task to perform when the job is run. Override when defining your own job type.
        
        This function should assume the job needs to be run. Checking if the job needs to be run should be handled by 
        overriding the `needs_to_run` method. This function also does not handle dependencies.
        
        For these reasons, you probably don't want to invoke this method directly when calling jobs (such as from tasks.py).
        You should probably use the `resolve` method instead.

        Args:
            c (Context): The pyinvoke Context from the current task invokation.
        """
        pass
    
    # Not to override:
    def depends_on(self, new_dependencies: list[JobBase]) -> JobBase:
        """Declare other jobs as dependencies for this one. 
        
        When resolving, these dependency jobs will also be resolved before this job is run.

        Args:
            new_dependencies (list[JobBase]): An iterable (preferably a list) containing the dependency jobs.

        Returns:
            JobBase: This method returns the object it's a member of.
        """
        self.dependencies.extend(new_dependencies)
        return self
    
    def resolve(self, c: Context, skip_dependencies: bool = False):
        """Invoke this method to actually process this job. First checks if the job needs to be run, then resolves dependencies and runs the job if so.
        
        A job is considered `resolved` after this method is called, regardless of whether the job actually ran. 
        
        Unless `self.no_duplication == True`, a job will not be resolved twice.

        Args:
            c (Context): The pyinvoke Context from the current task invokation.
            skip_dependencies (bool, optional): If True, skip handling dependency jobs. Defaults to False.
        """
        if self.no_duplication and self._has_been_resolved:
            return
        
        if self.needs_to_run(c):
            if not skip_dependencies:
                for i in self.dependencies:
                    i.resolve(c)
            self.run(c)
        
        self._has_been_resolved = True
        self._resolved_jobs.append(self)
        
    def get_recursive_mod_outputs(self, include_unresolved_jobs: bool = True, include_self: bool = True) -> dict[Path, Path]:
        """Get the combined mod_output_files from this job and all dependent jobs. By default, skips any dependent job that wasn't resolved.
        
        Used by specific job types to collect all files for build output folders and Thunderstore packaging.

        Args:
            include_unresolved_jobs (bool, optional): If True, skip any dependency job that wasn't resolved. Defaults to True.
            include_self (bool, optional): Include this job regardless of whether it was resolved. Defaults to True.

        Returns:
            dict[Path, Path]: The combined mod_output_files. The key will be the desired file location in the output, the value will be the path in the project.
        """
        if not (include_self or self._has_been_resolved or include_unresolved_jobs):
            return {}
        
        retVal = self.mod_output_files
        
        for i in self.dependencies:
            retVal.update(i.get_recursive_mod_outputs(include_unresolved_jobs, False))
        
        return retVal
    
    def add_mod_output_files(self, files: dict[Path, Path]):
        """Add additional mod_output_files in addition to what the job already declares.

        Args:
            files (dict[Path, Path]): The additional mod_output_files to declare. The key will be the desired file location in the output, the value will be the path in the project.
        """
        self.mod_output_files.update(files)