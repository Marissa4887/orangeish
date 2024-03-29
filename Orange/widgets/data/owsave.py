import os.path

from Orange.data.table import Table
from Orange.data.io import TabReader, CSVReader, PickleReader, ExcelReader
from Orange.widgets import gui, widget
from Orange.widgets.widget import Input
from Orange.widgets.settings import Setting
from Orange.widgets.utils.save.owsavebase import OWSaveBase
from Orange.widgets.utils.widgetpreview import WidgetPreview


_userhome = os.path.expanduser(f"~{os.sep}")


class OWSave(OWSaveBase):
    name = "Save Data"
    description = "Save data to an output file."
    icon = "icons/Save.svg"
    category = "Data"
    keywords = []

    settings_version = 2

    writers = [TabReader, CSVReader, PickleReader, ExcelReader]
    filters = {
        **{f"{w.DESCRIPTION} (*{w.EXTENSIONS[0]})": w
           for w in writers},
        **{f"Compressed {w.DESCRIPTION} (*{w.EXTENSIONS[0]}.gz)": w
           for w in writers if w.SUPPORT_COMPRESSED}
    }

    class Inputs:
        data = Input("Data", Table)

    class Error(OWSaveBase.Error):
        unsupported_sparse = widget.Msg("Use Pickle format for sparse data.")

    add_type_annotations = Setting(True)

    def __init__(self):
        super().__init__(2)

        self.grid.addWidget(
            gui.checkBox(
                None, self, "add_type_annotations",
                "Add type annotations to header",
                tooltip=
                "Some formats (Tab-delimited, Comma-separated) can include \n"
                "additional information about variables types in header rows.",
                callback=self.update_messages),
            0, 0, 1, 2)
        self.grid.setRowMinimumHeight(1, 8)
        self.adjustSize()

    @Inputs.data
    def dataset(self, data):
        self.data = data
        self.on_new_input()

    def do_save(self):
        if self.data.is_sparse() and not self.writer.SUPPORT_SPARSE_DATA:
            return
        self.writer.write(self.filename, self.data, self.add_type_annotations)

    def update_messages(self):
        super().update_messages()
        self.Error.unsupported_sparse(
            shown=self.data is not None and self.data.is_sparse()
            and self.filename and not self.writer.SUPPORT_SPARSE_DATA)

    def update_status(self):
        if self.data is None:
            self.info.set_input_summary(self.info.NoInput)
        else:
            self.info.set_input_summary(
                str(len(self.data)),
                f"Data set {self.data.name or '(no name)'} "
                f"with {len(self.data)} instances")

    def send_report(self):
        self.report_data_brief(self.data)
        writer = self.writer
        noyes = ["No", "Yes"]
        self.report_items((
            ("File name", self.filename or "not set"),
            ("Format", writer.DESCRIPTION),
            ("Type annotations",
             writer.OPTIONAL_TYPE_ANNOTATIONS
             and noyes[self.add_type_annotations])
        ))

    @classmethod
    def migrate_settings(cls, settings, version=0):
        def migrate_to_version_2():
            # Set the default; change later if possible
            settings.pop("compression", None)
            settings["filter"] = next(iter(cls.filters))
            filetype = settings.pop("filetype", None)
            if filetype is None:
                return

            ext = cls._extension_from_filter(filetype)
            if settings.pop("compress", False):
                for afilter in cls.filters:
                    if ext + ".gz" in afilter:
                        settings["filter"] = afilter
                        return
                # If not found, uncompressed may have been erroneously set
                # for a writer that didn't support if (such as .xlsx), so
                # fall through to uncompressed
            for afilter in cls.filters:
                if ext in afilter:
                    settings["filter"] = afilter
                    return

        if version < 2:
            migrate_to_version_2()

    def initial_start_dir(self):
        if self.filename and os.path.exists(os.path.split(self.filename)[0]):
            return self.filename
        else:
            data_name = getattr(self.data, 'name', '')
            if data_name:
                data_name += self.writer.EXTENSIONS[0]
            return os.path.join(self.last_dir or _userhome, data_name)

    def valid_filters(self):
        if self.data is None or not self.data.is_sparse():
            return self.filters
        else:
            return {filt: writer for filt, writer in self.filters.items()
                    if writer.SUPPORT_SPARSE_DATA}

    def default_valid_filter(self):
        if self.data is None or not self.data.is_sparse() \
                or self.filters[self.filter].SUPPORT_SPARSE_DATA:
            return self.filter
        for filt, writer in self.filters.items():
            if writer.SUPPORT_SPARSE_DATA:
                return filt
        # This shouldn't happen and it will trigger an error in tests
        return None   # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(OWSave).run(Table("iris"))
